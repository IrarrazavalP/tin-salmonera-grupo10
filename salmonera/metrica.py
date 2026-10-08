"""La métrica: costo de alimento por kg ganado, separado en precio, FCR y mortalidad.

    FCR biológico = alimento ÷ (biomasa ganada + biomasa muerta)   → eficiencia del alimento
    FCR económico = alimento ÷ biomasa ganada                       → lo que paga la empresa
    Costo por kg  = precio × FCR biológico × (1 + muerta ÷ ganada)  → igual a costo ÷ ganada

La biomasa muerta se separa en basal (lo normal) y exceso por evento sanitario,
así que el factor de mortalidad también se separa en dos.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import Decisiones
from .fuentes import Fuentes

ETAPAS = ("engorda 100", "engorda 200", "pigmentado")


@dataclass
class Resultado:
    decisiones: Decisiones
    hechos: pd.DataFrame          # una fila es una jaula en un día
    por_centro: pd.DataFrame
    basal: pd.DataFrame
    conciliacion: pd.DataFrame
    cosechas: pd.DataFrame
    descomposicion: pd.DataFrame
    centro_caro: str
    resumen: dict


# ------------------------------------------------------------ jaula-día
def etapa_por_peso(peso: pd.Series, d: Decisiones) -> pd.Series:
    return pd.Series(
        np.select([peso < d.corte_100, peso < d.corte_200], ["engorda 100", "engorda 200"], "pigmentado"),
        index=peso.index,
    )


def precios_clp(f: Fuentes) -> pd.DataFrame:
    """Lista de precios llevada a CLP/kg; las filas en dólares se convierten con el dólar promedio del mes."""
    p = f.precios.copy()
    dolar_mes = f.dolar.assign(mes=f.dolar["fecha"].dt.to_period("M")).groupby("mes")["valor"].mean()
    p["dolar"] = p["mes"].map(dolar_mes)
    p["precio_clp_kg"] = np.where(p["en_usd"], p["precio"] * p["dolar"], p["precio"])
    return p.dropna(subset=["precio_clp_kg"])


def _precio_del_mes(serie: pd.Series, meses: pd.Series) -> pd.Series:
    """Precio de cada mes; si un mes no tiene lista, se usa el último mes anterior con precio."""
    if serie.empty:
        return pd.Series(np.nan, index=meses.index)
    tabla = serie.sort_index()
    rango = pd.period_range(min(tabla.index.min(), meses.min()), max(tabla.index.max(), meses.max()), freq="M")
    tabla = tabla.reindex(rango).ffill().bfill()
    return meses.map(tabla)


def tabla_jaula_dia(f: Fuentes, d: Decisiones) -> pd.DataFrame:
    h = f.operacion.copy()
    h["mes"] = h["fecha"].dt.to_period("M")
    h["peso_kg"] = h["biomasa_kg"] / h["poblacion"]
    if d.peso_muerto == "dia_anterior":
        anterior = h.groupby("jaula_id")["peso_kg"].shift(1)
        h["peso_muerto_kg"] = anterior.fillna(h["peso_kg"])
    else:
        h["peso_muerto_kg"] = h["peso_kg"]
    h["muerta_kg"] = h["mortalidad_n"] * h["peso_muerto_kg"]
    h["etapa"] = etapa_por_peso(h["peso_kg"], d)

    p = precios_clp(f)
    if d.precio == "por_etapa":
        h["precio_clp_kg"] = np.nan
        for etapa in ETAPAS:
            serie = p[p["etapa"] == etapa].groupby("mes")["precio_clp_kg"].mean()
            filas = h["etapa"] == etapa
            h.loc[filas, "precio_clp_kg"] = _precio_del_mes(serie, h.loc[filas, "mes"]).values
        # Si una etapa no aparece en la lista de precios, se usa el promedio del mes.
        h["precio_clp_kg"] = h["precio_clp_kg"].fillna(_precio_del_mes(p.groupby("mes")["precio_clp_kg"].mean(), h["mes"]))
    else:
        h["precio_clp_kg"] = _precio_del_mes(p.groupby("mes")["precio_clp_kg"].mean(), h["mes"])
    h["costo_alimento_clp"] = h["alimento_kg"] * h["precio_clp_kg"]
    return h


# ------------------------------------------------------------- eventos
def marcar_eventos(h: pd.DataFrame, f: Fuentes, d: Decisiones) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Marca cada jaula-día que cae en la ventana de un evento y arma el detalle evento × jaula."""
    jaulas_por_centro = h.groupby("centro_id")["jaula_id"].unique()
    ultima = h["fecha"].max()
    filas = []
    for ev in f.eventos.itertuples():
        jaulas = list(ev.jaulas)
        if not jaulas:
            if d.sin_jaulas == "excluir":
                continue
            jaulas = list(jaulas_por_centro.get(ev.centro_id, []))
        inicio = pd.Timestamp(ev.inicio) - pd.to_timedelta(int(d.ventana_previa_dias), unit="D")
        fin = ev.fin if pd.notna(ev.fin) else ultima
        for j in jaulas:
            filas.append({"evento_id": ev.evento_id, "jaula_id": j, "desde": inicio, "hasta": fin})
    ventanas = pd.DataFrame(filas, columns=["evento_id", "jaula_id", "desde", "hasta"])

    h = h.copy()
    h["evento_id"] = None
    for v in ventanas.itertuples():
        en = (h["jaula_id"] == v.jaula_id) & h["fecha"].between(v.desde, v.hasta) & h["evento_id"].isna()
        h.loc[en, "evento_id"] = v.evento_id
    h["con_evento"] = h["evento_id"].notna()
    return h, ventanas


def mortalidad_basal(h: pd.DataFrame, d: Decisiones) -> pd.DataFrame:
    """Tasa diaria normal (peces muertos ÷ población) en jaula-días sin evento declarado."""
    sin = h[~h["con_evento"]]
    clave = "etapa" if d.basal == "por_etapa" else None
    if clave:
        tasa = sin.groupby(clave).agg(muertos=("mortalidad_n", "sum"), poblacion=("poblacion", "sum"))
    else:
        tasa = pd.DataFrame({"muertos": [sin["mortalidad_n"].sum()], "poblacion": [sin["poblacion"].sum()]},
                            index=pd.Index(["global"], name="etapa"))
    tasa["tasa_diaria"] = tasa["muertos"] / tasa["poblacion"]
    return tasa.reset_index()


def exceso_por_evento(h: pd.DataFrame, basal: pd.DataFrame, d: Decisiones) -> pd.DataFrame:
    h = h.copy()
    if d.basal == "por_etapa":
        tasas = dict(zip(basal["etapa"], basal["tasa_diaria"]))
        global_ = basal["muertos"].sum() / basal["poblacion"].sum()
        h["tasa_basal"] = h["etapa"].map(tasas).fillna(global_)
    else:
        h["tasa_basal"] = float(basal["tasa_diaria"].iloc[0])
    h["mortalidad_basal_n"] = h["poblacion"] * h["tasa_basal"]
    h["exceso_n"] = np.where(h["con_evento"], (h["mortalidad_n"] - h["mortalidad_basal_n"]).clip(lower=0), 0.0)
    h["exceso_kg"] = h["exceso_n"] * h["peso_muerto_kg"]
    return h


def conciliar(h: pd.DataFrame, f: Fuentes, ventanas: pd.DataFrame) -> pd.DataFrame:
    """Mortalidad declarada por sanidad vs. la que suma la operación diaria en la misma ventana."""
    filas = []
    for ev in f.eventos.itertuples():
        v = ventanas[ventanas["evento_id"] == ev.evento_id]
        dias = h[h["evento_id"] == ev.evento_id]
        filas.append({
            "evento_id": ev.evento_id,
            "centro_id": ev.centro_id,
            "tipo": ev.tipo,
            "jaulas_identificadas": len(ev.jaulas),
            "jaulas_en_ventana": v["jaula_id"].nunique(),
            "mortalidad_declarada_n": ev.mortalidad_declarada,
            "mortalidad_diaria_n": dias["mortalidad_n"].sum(),
            "exceso_sobre_basal_n": dias["exceso_n"].sum(),
            "peso_medio_kg": dias["peso_muerto_kg"].mean(),
        })
    return pd.DataFrame(filas)


# ----------------------------------------------------------- biomasa ganada
def biomasa_ganada(h: pd.DataFrame, f: Fuentes, d: Decisiones) -> pd.DataFrame:
    """Crecimiento bruto y biomasa ganada neta por jaula.

    `crecimiento_kg` es bruto: en el registro, biomasa de hoy − biomasa de ayer
    + peso de los muertos = crecimiento (calza en el 99 % de los días). Por eso:
        crecimiento bruto = Σ crecimiento_kg          → denominador del FCR biológico
        ganada neta       = crecimiento bruto − muerta → denominador del FCR económico
    La alternativa "balance" usa biomasa final − inicial como ganada neta.
    Las cosechas no se suman: el registro diario no las descuenta (ver conciliación).
    """
    g = h.groupby(["centro_id", "jaula_id"]).agg(
        biomasa_inicial_kg=("biomasa_kg", "first"),
        biomasa_ultima_kg=("biomasa_kg", "last"),
        crecimiento_registrado_kg=("crecimiento_kg", "sum"),
        muerta_kg=("muerta_kg", "sum"),
    ).reset_index()
    if d.ganancia == "balance":
        g["ganada_kg"] = g["biomasa_ultima_kg"] - g["biomasa_inicial_kg"]
    else:
        g["ganada_kg"] = g["crecimiento_registrado_kg"] - g["muerta_kg"]
    return g.drop(columns=["muerta_kg"])


def conciliar_cosechas(f: Fuentes) -> pd.DataFrame:
    """Cuarta tabla de la base: cada cosecha frente al registro diario de su jaula."""
    h = f.operacion
    filas = []
    for c in f.cosechas.itertuples():
        s = h[h["jaula_id"] == c.jaula_id]
        dia = s[s["fecha"] <= c.fecha].tail(1)
        filas.append({
            "lote_id": c.lote_id,
            "jaula_id": c.jaula_id,
            "fecha_cosecha": c.fecha.date(),
            "kilos_vivos": c.kilos_vivos,
            "biomasa_registrada_ese_dia_kg": float(dia["biomasa_kg"].iloc[0]) if len(dia) else np.nan,
            "dias_de_registro_despues": int((s["fecha"] > c.fecha).sum()),
        })
    return pd.DataFrame(filas)


# ------------------------------------------------------------ por centro
def por_centro(h: pd.DataFrame, ganancia: pd.DataFrame, f: Fuentes, d: Decisiones) -> pd.DataFrame:
    c = h.groupby("centro_id").agg(
        alimento_kg=("alimento_kg", "sum"),
        costo_alimento_clp=("costo_alimento_clp", "sum"),
        muerta_kg=("muerta_kg", "sum"),
        exceso_evento_kg=("exceso_kg", "sum"),
        jaula_dias=("fecha", "size"),
    )
    gan = ganancia.groupby("centro_id").agg(
        ganada_kg=("ganada_kg", "sum"),
        biomasa_final_kg=("biomasa_ultima_kg", "sum"),
        crecimiento_registrado_kg=("crecimiento_registrado_kg", "sum"),
    )
    c = c.join(gan)
    if d.mortalidad == "sanidad":
        # Se reemplaza el exceso medido por la mortalidad declarada, valorizada al peso medio de la ventana.
        dec = f.eventos.assign(centro_id=f.eventos["centro_id"])
        peso = h[h["con_evento"]].groupby("evento_id")["peso_muerto_kg"].mean()
        dec["kg"] = dec["mortalidad_declarada"].fillna(0) * dec["evento_id"].map(peso).fillna(h["peso_muerto_kg"].mean())
        c["exceso_evento_kg"] = dec.groupby("centro_id")["kg"].sum().reindex(c.index).fillna(0.0)
        c["exceso_evento_kg"] = c[["exceso_evento_kg", "muerta_kg"]].min(axis=1)
    c["muerta_basal_kg"] = c["muerta_kg"] - c["exceso_evento_kg"]
    return agregar_indicadores(c, f)


def agregar_indicadores(c: pd.DataFrame, f: Fuentes) -> pd.DataFrame:
    c = c.copy()
    c["precio_medio_clp_kg"] = c["costo_alimento_clp"] / c["alimento_kg"]
    c["fcr_economico"] = c["alimento_kg"] / c["ganada_kg"]
    c["fcr_biologico"] = c["alimento_kg"] / (c["ganada_kg"] + c["muerta_kg"])
    c["fcr_bruto_gerencia"] = c["alimento_kg"] / c["biomasa_final_kg"]
    c["factor_mortalidad"] = 1 + c["muerta_kg"] / c["ganada_kg"]
    c["costo_clp_por_kg"] = c["costo_alimento_clp"] / c["ganada_kg"]
    c["costo_mortalidad_evento_clp"] = c["exceso_evento_kg"] * c["fcr_biologico"] * c["precio_medio_clp_kg"]
    c["costo_mortalidad_total_clp"] = c["muerta_kg"] * c["fcr_biologico"] * c["precio_medio_clp_kg"]
    dolar = f.dolar["valor"].mean()
    c["costo_usd_por_kg"] = c["costo_clp_por_kg"] / dolar
    c["costo_mortalidad_evento_usd"] = c["costo_mortalidad_evento_clp"] / dolar
    return c.replace([np.inf, -np.inf], np.nan)


def descomponer(c: pd.DataFrame, caro: str) -> pd.DataFrame:
    """Cuánto de la diferencia de costo por kg (centro caro vs. el resto) aporta cada factor.

    Costo/kg = precio × FCR biológico × M_basal × M_evento, con
    M_basal = 1 + basal/ganada y M_evento = (1 + muerta/ganada) / M_basal.
    El logaritmo convierte el producto en suma y reparte la diferencia sin residuo.
    """
    resto = c.drop(index=caro).sum(numeric_only=True)
    def factores(s: pd.Series) -> dict[str, float]:
        m_basal = 1 + s["muerta_basal_kg"] / s["ganada_kg"]
        m_total = 1 + s["muerta_kg"] / s["ganada_kg"]
        return {
            "precio del alimento": s["costo_alimento_clp"] / s["alimento_kg"],
            "eficiencia (FCR biológico)": s["alimento_kg"] / (s["ganada_kg"] + s["muerta_kg"]),
            "mortalidad basal": m_basal,
            "mortalidad por evento sanitario": m_total / m_basal,
        }
    fa, fr = factores(c.loc[caro]), factores(resto)
    costo_a = c.loc[caro, "costo_alimento_clp"] / c.loc[caro, "ganada_kg"]
    costo_r = resto["costo_alimento_clp"] / resto["ganada_kg"]
    diferencia = costo_a - costo_r
    total_log = math.log(costo_a / costo_r) if costo_a > 0 and costo_r > 0 and costo_a != costo_r else 0.0
    filas = []
    for k in fa:
        parte = math.log(fa[k] / fr[k]) / total_log if total_log else 0.0
        filas.append({"factor": k, "centro_caro": fa[k], "resto": fr[k],
                      "aporte_clp_por_kg": parte * diferencia, "aporte_pct": 100 * parte})
    return pd.DataFrame(filas)


def cortar_post_cosecha(h: pd.DataFrame, f: Fuentes) -> pd.DataFrame:
    cosecha = f.cosechas.groupby("jaula_id")["fecha"].min()
    limite = h["jaula_id"].map(cosecha)
    return h[limite.isna() | (h["fecha"] <= limite)].copy()


def calcular(f: Fuentes, d: Decisiones) -> Resultado:
    h = tabla_jaula_dia(f, d)
    if d.post_cosecha == "cortar":
        h = cortar_post_cosecha(h, f)
    h, ventanas = marcar_eventos(h, f, d)
    basal = mortalidad_basal(h, d)
    h = exceso_por_evento(h, basal, d)
    ganancia = biomasa_ganada(h, f, d)
    c = por_centro(h, ganancia, f, d)
    validos = c[c["ganada_kg"] > 0]
    caro = validos["costo_clp_por_kg"].idxmax()
    desc = descomponer(validos, caro)
    fila = c.loc[caro]
    aporte = dict(zip(desc["factor"], desc["aporte_pct"]))
    resumen = {
        "centro_mas_caro": caro,
        "costo_clp_por_kg_centro": round(float(fila["costo_clp_por_kg"]), 1),
        "costo_clp_por_kg_resto": round(float(
            c.drop(index=caro)["costo_alimento_clp"].sum() / c.drop(index=caro)["ganada_kg"].sum()), 1),
        "fcr_biologico_centro": round(float(fila["fcr_biologico"]), 3),
        "fcr_economico_centro": round(float(fila["fcr_economico"]), 3),
        "aporte_pct_precio": round(aporte["precio del alimento"], 1),
        "aporte_pct_fcr": round(aporte["eficiencia (FCR biológico)"], 1),
        "aporte_pct_mortalidad_basal": round(aporte["mortalidad basal"], 1),
        "aporte_pct_mortalidad_evento": round(aporte["mortalidad por evento sanitario"], 1),
        "costo_mortalidad_evento_clp_centro": round(float(fila["costo_mortalidad_evento_clp"])),
        "costo_mortalidad_evento_clp_total": round(float(c["costo_mortalidad_evento_clp"].sum())),
    }
    return Resultado(d, h, c, basal, conciliar(h, f, ventanas), conciliar_cosechas(f), desc, caro, resumen)
