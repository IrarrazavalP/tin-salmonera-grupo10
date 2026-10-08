"""Lectura y limpieza de las cuatro fuentes del caso.

1. origen_acuicultura.sqlite   — maestros, operación diaria por jaula y cosechas
2. origen_costos_alimento.csv  — lista de precios de Abastecimiento (';', latin-1)
3. origen_eventos_sanitarios.json — eventos de sanidad, con jaulas afectadas anidadas
4. API de mindicador.cl        — dólar observado, para llevar precios y resultados a USD
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests

from .config import ARCHIVOS_CASO, CACHE, DATOS, REPO_CURSO
from .limpieza import Cobertura, a_entero, a_fecha, a_id, a_mes, a_numero, es_basura


def _archivo(carpeta: Path, patron: str) -> Path:
    candidatos = sorted(carpeta.glob(patron))
    if not candidatos:
        raise FileNotFoundError(
            f"No encontré {patron} en {carpeta}. Copia ahí los archivos del caso (grupo_s3); ver README."
        )
    return candidatos[0]


@dataclass
class Fuentes:
    centros: pd.DataFrame
    jaulas: pd.DataFrame
    lotes: pd.DataFrame
    operacion: pd.DataFrame
    cosechas: pd.DataFrame
    precios: pd.DataFrame
    eventos: pd.DataFrame
    dolar: pd.DataFrame
    cobertura: Cobertura
    origen_dolar: str


# ----------------------------------------------------------------- SQLite
def leer_sqlite(ruta: Path) -> dict[str, pd.DataFrame]:
    with sqlite3.connect(ruta) as con:
        nombres = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", con)["name"]
        return {n: pd.read_sql(f'SELECT * FROM "{n}"', con) for n in nombres}


def limpiar_operacion(op: pd.DataFrame, jaulas: pd.DataFrame, cob: Cobertura) -> pd.DataFrame:
    total = len(op)
    df = pd.DataFrame({
        "fecha": op["fecha"].map(a_fecha),
        "centro_id": op["centro_id"].map(a_id) if "centro_id" in op else None,
        "jaula_id": op["jaula_id"].map(a_id),
        "lote_id": op["lote_id"].map(a_id) if "lote_id" in op else None,
        "alimento_kg": op["alimento_kg"].map(a_numero),
        "mortalidad_n": op["mortalidad_n"].map(a_entero),
        "poblacion": op["poblacion"].map(a_entero),
        "biomasa_kg": op["biomasa_kg"].map(a_numero),
        "crecimiento_kg": op["crecimiento_kg"].map(a_numero) if "crecimiento_kg" in op else None,
        "temperatura_agua": op["temperatura_agua"].map(lambda v: a_numero(v, miles_posible=False))
        if "temperatura_agua" in op else None,
    })
    # El centro se recupera desde el maestro de jaulas cuando falta en el registro.
    mapa_centro = dict(zip(jaulas["jaula_id"].map(a_id), jaulas["centro_id"].map(a_id)))
    df["centro_id"] = df["centro_id"].fillna(df["jaula_id"].map(mapa_centro))

    motivos: dict[str, int] = {}

    def fuera(mascara: pd.Series, motivo: str) -> None:
        nonlocal df
        n = int(mascara.sum())
        if n:
            motivos[motivo] = n
            df = df[~mascara]

    fuera(df["fecha"].isna(), "fecha ilegible o vacía")
    fuera(df["jaula_id"].isna() | df["centro_id"].isna(), "sin jaula o centro identificable")
    criticas = ["alimento_kg", "mortalidad_n", "poblacion", "biomasa_kg"]
    fuera(df[criticas].isna().any(axis=1), "alimento, mortalidad, población o biomasa ilegible")
    fuera((df["poblacion"] <= 0) | (df["biomasa_kg"] <= 0), "población o biomasa en cero o negativa")
    fuera((df["alimento_kg"] < 0) | (df["mortalidad_n"] < 0), "alimento o mortalidad negativa")
    fuera(df.duplicated(["jaula_id", "fecha"], keep="first"), "registro duplicado jaula-día")
    cob.registrar("operacion_diaria", total, motivos)
    df = df.sort_values(["jaula_id", "fecha"]).reset_index(drop=True)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return corregir_mortalidad(df, cob)


def corregir_mortalidad(df: pd.DataFrame, cob: Cobertura, umbral: int = 1000) -> pd.DataFrame:
    """Mortalidad mal digitada: la población del día siguiente manda.

    En el registro, la población de un día ya descuenta los muertos del día
    anterior (pasa en el 98 % de los días). Si un día declara al menos `umbral`
    muertos y la población del día siguiente no cae en esa cantidad, se reemplaza
    por la caída real de población.
    """
    df = df.copy()
    g = df.groupby("jaula_id")
    siguiente = g["poblacion"].shift(-1)
    consecutivo = (g["fecha"].shift(-1) - df["fecha"]).dt.days == 1
    caida = df["poblacion"] - siguiente
    mal = (
        (df["mortalidad_n"] >= umbral)
        & consecutivo
        & (caida >= 0)
        & ((caida - df["mortalidad_n"]).abs() > 0.01 * df["mortalidad_n"])
    )
    df["mortalidad_corregida"] = mal
    df.loc[mal, "mortalidad_n"] = caida[mal]
    cob.corregir("operacion_diaria", "mortalidad que no calza con la caída de población del día siguiente", int(mal.sum()))
    return df


def limpiar_cosechas(cos: pd.DataFrame, lotes: pd.DataFrame, cob: Cobertura) -> pd.DataFrame:
    total = len(cos)
    df = pd.DataFrame({
        "lote_id": cos["lote_id"].map(a_id),
        "centro_id": cos["centro_id"].map(a_id) if "centro_id" in cos else None,
        "fecha": cos["fecha"].map(a_fecha),
        "kilos_vivos": cos["kilos_vivos"].map(a_numero),
    })
    df["jaula_id"] = df["lote_id"].map(dict(zip(lotes["lote_id"], lotes["jaula_id"])))
    motivos = {}
    malas = df["fecha"].isna() | df["kilos_vivos"].isna() | (df["kilos_vivos"] <= 0)
    if malas.sum():
        motivos["fecha o kilos vivos ilegibles"] = int(malas.sum())
    sin_jaula = ~malas & df["jaula_id"].isna()
    if sin_jaula.sum():
        motivos["lote sin jaula en el maestro"] = int(sin_jaula.sum())
    cob.registrar("cosechas", total, motivos)
    df = df[~malas & ~sin_jaula].copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


# -------------------------------------------------------------------- CSV
def leer_precios(ruta: Path, cob: Cobertura) -> pd.DataFrame:
    try:
        crudo = pd.read_csv(ruta, sep=";", dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        crudo = pd.read_csv(ruta, sep=";", dtype=str, encoding="latin-1")
    crudo.columns = [c.strip().lower() for c in crudo.columns]
    col_precio = next(c for c in crudo.columns if c.startswith("precio"))
    df = pd.DataFrame({
        "tipo": crudo["tipo_alimento"].map(lambda v: None if es_basura(v) else str(v).strip()),
        "mes": crudo["mes"].map(a_mes),
        "precio": crudo[col_precio].map(a_numero),
        "moneda": crudo["moneda"].fillna("CLP").str.strip().str.upper() if "moneda" in crudo else "CLP",
    })
    malas = df[["tipo", "mes", "precio"]].isna().any(axis=1) | (df["precio"] <= 0)
    cob.registrar("costos_alimento", len(df), {"tipo, mes o precio ilegible": int(malas.sum())} if malas.sum() else {})
    df = df[~malas].copy()
    df["en_usd"] = df["moneda"].str.contains("USD|US\\$|DOL", regex=True)
    df["etapa"] = df["tipo"].map(etapa_de_tipo)
    return df


def etapa_de_tipo(tipo: str) -> str:
    t = tipo.lower()
    if t.startswith("pig"):
        return "pigmentado"
    if "200" in t:
        return "engorda 200"
    if "100" in t:
        return "engorda 100"
    return "otro"


# ------------------------------------------------------------------- JSON
def leer_eventos(ruta: Path, cob: Cobertura, centros_validos: set[str] | None = None) -> pd.DataFrame:
    """Un renglón por evento, con su lista de jaulas (vacía si no vienen identificadas)."""
    crudo = json.loads(ruta.read_text(encoding="utf-8"))
    eventos = crudo["eventos"] if isinstance(crudo, dict) else crudo
    filas = []
    for ev in eventos:
        jaulas = ev.get("jaulas_afectadas") or []
        jaulas = [a_id(j.get("jaula_id") if isinstance(j, dict) else j) for j in jaulas]
        filas.append({
            "evento_id": a_id(ev.get("evento_id")),
            "centro_id": a_id(ev.get("centro_id")),
            "tipo": ev.get("tipo"),
            "inicio": a_fecha(ev.get("fecha_inicio")),
            "fin": a_fecha(ev.get("fecha_fin")),
            "mortalidad_declarada": a_entero(ev.get("mortalidad_asociada")),
            "jaulas": [j for j in jaulas if j],
        })
    df = pd.DataFrame(filas)
    motivos = {}
    malos = df["inicio"].isna() | df["centro_id"].isna()
    if malos.sum():
        motivos["sin fecha de inicio o centro"] = int(malos.sum())
    if centros_validos is not None:
        ajenos = ~malos & ~df["centro_id"].isin(centros_validos)
        if ajenos.sum():
            motivos["centro que no existe en la base de operaciones"] = int(ajenos.sum())
        malos = malos | ajenos
    cob.registrar("eventos_sanitarios", len(df), motivos)
    df = df[~malos].copy()
    df["inicio"] = pd.to_datetime(df["inicio"])
    df["fin"] = pd.to_datetime(df["fin"])
    return df


# -------------------------------------------------------------------- API
def leer_dolar(anios: list[int], cob: Cobertura) -> tuple[pd.DataFrame, str]:
    """Dólar observado diario desde mindicador.cl, con copia en data/cache por si la API no responde."""
    CACHE.mkdir(parents=True, exist_ok=True)
    series, origenes = [], set()
    for anio in anios:
        copia = CACHE / f"dolar_{anio}.json"
        try:
            r = requests.get(f"https://mindicador.cl/api/dolar/{anio}", timeout=30)
            r.raise_for_status()
            serie = r.json()["serie"]
            copia.write_text(json.dumps(serie), encoding="utf-8")
            origenes.add("API en vivo")
        except (requests.RequestException, KeyError, ValueError):
            if not copia.exists():
                raise RuntimeError(f"mindicador.cl no respondió para {anio} y no hay copia en {copia}")
            serie = json.loads(copia.read_text(encoding="utf-8"))
            origenes.add("copia local (API sin respuesta)")
        series.extend(serie)
    df = pd.DataFrame(series)
    df["fecha"] = pd.to_datetime(df["fecha"].str[:10])
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    malos = df["valor"].isna()
    cob.registrar("mindicador_dolar", len(df), {"valor vacío": int(malos.sum())} if malos.sum() else {})
    return df[~malos][["fecha", "valor"]], " + ".join(sorted(origenes))


def descargar_caso(carpeta: Path) -> list[str]:
    """Baja del repositorio del curso los archivos que falten en `carpeta`."""
    carpeta.mkdir(parents=True, exist_ok=True)
    bajados = []
    for nombre in ARCHIVOS_CASO:
        destino = carpeta / nombre
        if destino.exists():
            continue
        r = requests.get(f"{REPO_CURSO}/{nombre}", timeout=60)
        r.raise_for_status()
        destino.write_bytes(r.content)
        bajados.append(nombre)
    return bajados


def cargar(carpeta: Path = DATOS) -> Fuentes:
    cob = Cobertura()
    tablas = leer_sqlite(_archivo(carpeta, "*.sqlite"))
    centros = tablas["centros"].assign(centro_id=lambda d: d["centro_id"].map(a_id))
    jaulas = tablas["jaulas"].assign(
        jaula_id=lambda d: d["jaula_id"].map(a_id), centro_id=lambda d: d["centro_id"].map(a_id)
    )
    lotes = tablas["lotes"].assign(
        lote_id=lambda d: d["lote_id"].map(a_id), jaula_id=lambda d: d["jaula_id"].map(a_id)
    )
    operacion = limpiar_operacion(tablas["operacion_diaria"], jaulas, cob)
    cosechas = limpiar_cosechas(tablas["cosechas"], lotes, cob)
    precios = leer_precios(_archivo(carpeta, "*.csv"), cob)
    eventos = leer_eventos(_archivo(carpeta, "*.json"), cob, set(centros["centro_id"]))
    anios = sorted({*operacion["fecha"].dt.year.unique(), *[p.year for p in precios["mes"]]})
    dolar, origen = leer_dolar([int(a) for a in anios], cob)
    return Fuentes(centros, jaulas, lotes, operacion, cosechas, precios, eventos, dolar, cob, origen)
