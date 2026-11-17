"""Pruebas de calidad de la cadena (componente B de la Entrega 2).

Corren en cada ejecución de entrega2.ipynb, sobre los datos reales del caso. Cada prueba deja una fila con
qué verifica, qué hace si falla y su resultado:

- OK     la prueba pasó (está dentro de su umbral).
- AVISO  la prueba no pasó y su acción es «avisa»: la corrida sigue y el problema queda registrado.
- FALLA  la prueba no pasó y su acción es «bloquea»: la corrida no publica results/.

Los problemas conocidos del caso (duplicados, registros posteriores a la cosecha, eventos de centros que no
existen) se detectan, se tratan y se cuentan en la cobertura; la prueba pasa si quedaron tratados y contados.
"""
import json
import sqlite3
from pathlib import Path

import pandas as pd

BLOQUEA, AVISA = "bloquea", "avisa"

TABLAS_SQLITE = ["zonas", "centros", "jaulas", "especies", "lotes", "operacion_diaria", "cosechas"]
COLUMNAS_OPERACION = ["fecha", "lote_id", "alimento_kg", "mortalidad_n", "poblacion", "biomasa_kg", "crecimiento_kg"]
COLUMNAS_CSV = ["tipo_alimento", "mes", "precio_clp_kg", "moneda"]
CLAVES_JSON = ["empresa", "anio", "eventos"]
CLAVES_EVENTO = ["evento_id", "centro_id", "tipo", "fecha_inicio", "fecha_fin", "mortalidad_asociada", "jaulas_afectadas"]


class RegistroCalidad:
    """Acumula el resultado de cada prueba de la corrida."""

    def __init__(self):
        self.filas = []

    def registrar(self, id_prueba, grupo, fuente, verifica, accion, umbral, prueba):
        """`prueba` es una función sin argumentos que devuelve (pasó, valor obtenido)."""
        try:
            paso, valor = prueba()
        except Exception as error:   # una prueba que no se puede evaluar cuenta como no pasada
            paso, valor = False, f"no se pudo evaluar: {type(error).__name__}: {error}"
        resultado = "OK" if paso else ("FALLA" if accion == BLOQUEA else "AVISO")
        self.filas.append({"id": id_prueba, "grupo": grupo, "fuente": fuente, "verifica": verifica,
                           "accion_si_falla": accion, "umbral": umbral, "valor": str(valor), "resultado": resultado})
        marca = {"OK": "  ok   ", "AVISO": " AVISO ", "FALLA": " FALLA "}[resultado]
        print(f"[{marca}] {id_prueba} {verifica} -> {valor}")

    def tabla(self):
        return pd.DataFrame(self.filas, columns=["id", "grupo", "fuente", "verifica", "accion_si_falla", "umbral",
                                                 "valor", "resultado"])

    def hay_bloqueo(self):
        return any(f["resultado"] == "FALLA" for f in self.filas)

    def resumen(self):
        t = self.tabla()
        total = len(t)
        ok = int((t["resultado"] == "OK").sum())
        bloqueantes = t[t["accion_si_falla"] == BLOQUEA]
        return {"total": total, "ok": ok, "aviso": int((t["resultado"] == "AVISO").sum()),
                "falla": int((t["resultado"] == "FALLA").sum()),
                "pct_ok": round(100 * ok / total, 1) if total else None,
                "bloqueantes_ok": bool((bloqueantes["resultado"] == "OK").all()),
                "no_pasaron": t.loc[t["resultado"] != "OK", "id"].tolist()}


# ---------------------------------------------------------------- antes de leer: las fuentes existen y tienen forma

def pruebas_previas(reg, data):
    """Fuentes que sostienen la métrica: si faltan o cambió su estructura, la corrida se detiene antes de leer."""
    data = Path(data)
    sqlite_path = data / "origen_acuicultura.sqlite"

    def f01():
        if not sqlite_path.exists():
            return False, "no existe el archivo"
        with sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True) as con:
            tablas = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        faltan = [t for t in TABLAS_SQLITE if t not in tablas]
        return not faltan, f"{len(TABLAS_SQLITE) - len(faltan)} de {len(TABLAS_SQLITE)} tablas" + (f"; faltan {faltan}" if faltan else "")

    def f02():
        with sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True) as con:
            columnas = {r[1] for r in con.execute("PRAGMA table_info(operacion_diaria)")}
        faltan = [c for c in COLUMNAS_OPERACION if c not in columnas]
        return not faltan, "completas" if not faltan else f"faltan {faltan}"

    def f05():
        csv = pd.read_csv(data / "origen_costos_alimento.csv", sep=";", encoding="latin-1", dtype=str)
        faltan = [c for c in COLUMNAS_CSV if c not in csv.columns]
        return not faltan, f"{len(csv)} filas; columnas completas" if not faltan else f"faltan {faltan}"

    def f09():
        with open(data / "origen_eventos_sanitarios.json", encoding="utf-8") as f:
            crudo = json.load(f)
        faltan = [c for c in CLAVES_JSON if c not in crudo]
        if faltan:
            return False, f"faltan {faltan}"
        incompletos = [e.get("evento_id") for e in crudo["eventos"] if any(c not in e for c in CLAVES_EVENTO)]
        return not incompletos, f"{len(crudo['eventos'])} eventos; incompletos: {incompletos or 'ninguno'}"

    reg.registrar("F-01", "fuente", "SQLite", "El archivo existe, abre y trae las 7 tablas", BLOQUEA, "7 de 7", f01)
    reg.registrar("F-02", "fuente", "SQLite", "operacion_diaria trae las columnas que usa la métrica", BLOQUEA, "todas", f02)
    reg.registrar("F-05", "fuente", "CSV costos", "Se lee con «;» y latin-1 y trae tipo, mes, precio y moneda", BLOQUEA, "todas", f05)
    reg.registrar("F-09", "fuente", "JSON eventos", "Estructura {empresa, anio, eventos} y cada evento completo", BLOQUEA, "completa", f09)


# ---------------------------------------------------------------- API

def prueba_api(reg, origen_por_anio):
    """F-13: el dólar vino de la API para todos los años. Si no, la cadena usó la copia guardada (decisión 3)."""
    def f13():
        return all(v == "API" for v in origen_por_anio.values()), origen_por_anio
    reg.registrar("F-13", "fuente", "API mindicador.cl", "Respuesta válida de la API para cada año (si no, copia guardada)",
                  AVISA, "todos los años desde la API", f13)


# ---------------------------------------------------------------- fuentes, ya leídas

def pruebas_fuentes(reg, operacion_diaria, cosechas, lotes, productos, dim_costos, operacion_limpia, crudo_eventos,
                    eventos, eventos_activos, tabla_cobertura, filas_csv, periodo):
    inicio, fin = (pd.Timestamp(x) for x in periodo)

    def f03():
        malas = {"operacion_diaria.fecha": int(operacion_diaria["fecha"].isna().sum()),
                 "cosechas.fecha": int(cosechas["fecha"].isna().sum()),
                 "lotes.fecha_siembra": int(lotes["fecha_siembra"].isna().sum())}
        return sum(malas.values()) == 0, malas

    def f04():
        malas = {c: int(operacion_diaria[c].isna().sum()) for c in ["alimento_kg", "biomasa_kg", "crecimiento_kg"]}
        malas["mortalidad_n"] = int(operacion_limpia["mortalidad_n"].isna().sum())
        malas["kilos_vivos"] = int(cosechas["kilos_vivos"].isna().sum())
        return sum(malas.values()) == 0, malas

    def f06():
        meses = set(operacion_limpia["fecha_dt"].dt.strftime("%m/%Y"))
        con_precio = set(dim_costos.loc[dim_costos["precio_promedio_clp"] > 0, "mes"])
        faltan = sorted(meses - con_precio)
        return not faltan, f"{len(meses) - len(faltan)} de {len(meses)} meses con precio" + (f"; faltan {faltan}" if faltan else "")

    def f07():
        monedas = sorted(productos["moneda"].dropna().str.strip().str.upper().unique())
        return monedas == ["CLP"], monedas

    def f08():
        descartadas = filas_csv - len(productos)
        return descartadas / filas_csv <= 0.15, f"{descartadas} de {filas_csv} filas descartadas"

    def f10():
        ini = pd.to_datetime(eventos["fecha_inicio"], format="%d/%m/%Y")
        fin_ev = pd.to_datetime(eventos["fecha_fin"], format="%d/%m/%Y")
        malos = int(((ini > fin_ev) | (ini < inicio) | (fin_ev > fin)).sum())
        return malos == 0, f"{malos} eventos con fechas invertidas o fuera del período"

    def f11():
        excluidos = len(crudo_eventos["eventos"]) - len(eventos)
        contados = int(tabla_cobertura.query("fuente == 'eventos_sanitarios'")["registros"].sum())
        return excluidos == contados and len(eventos) > 0, f"{excluidos} de {len(crudo_eventos['eventos'])} excluidos y contados en la cobertura"

    def f12():
        con_jaulas = set(eventos_activos["evento_id"]) if len(eventos_activos) else set()
        sin = sorted(set(eventos["evento_id"]) - con_jaulas)
        return not sin, f"{len(con_jaulas)} de {len(eventos)} eventos alcanzan jaulas" + (f"; sin jaulas: {sin}" if sin else "")

    reg.registrar("F-03", "fuente", "SQLite", "Todas las fechas se leen en alguno de los 4 formatos", AVISA, "0 ilegibles", f03)
    reg.registrar("F-04", "fuente", "SQLite", "Los números (punto de miles, coma decimal) se leen", AVISA, "0 ilegibles", f04)
    reg.registrar("F-06", "fuente", "CSV costos", "Cada mes de operación tiene precio > 0", BLOQUEA, "todos los meses", f06)
    reg.registrar("F-07", "fuente", "CSV costos", "Todos los precios vienen en CLP", AVISA, "solo CLP", f07)
    reg.registrar("F-08", "fuente", "CSV costos", "Filas descartadas (títulos, TOTAL, «sin dato») dentro de lo esperado", AVISA, "≤ 15 %", f08)
    reg.registrar("F-10", "fuente", "JSON eventos", "Inicio ≤ fin y ambas fechas dentro del período", AVISA, "0 casos", f10)
    reg.registrar("F-11", "fuente", "JSON eventos", "Eventos de centros que no existen: excluidos y contados", AVISA, "todos contados", f11)
    reg.registrar("F-12", "fuente", "JSON eventos", "Cada evento válido alcanza al menos una jaula (decisiones 6 y 9)", AVISA, "todos", f12)


# ---------------------------------------------------------------- tabla de hechos (una fila = una jaula en un día)

def pruebas_hechos(reg, hechos, lotes, jaulas, centros, especies, cosechas, cosechas_validas, por_lote,
                   tabla_cobertura, total_op, comprobaciones, periodo):
    inicio, fin = (pd.Timestamp(x) for x in periodo)

    def h01():
        dup = int(hechos.duplicated(["lote_id", "fecha_dt"]).sum())
        return dup == 0, f"{dup} duplicados de (lote, fecha) en {len(hechos)} filas"

    def h02():
        huerfanos = {
            "lote": int((~hechos["lote_id"].isin(lotes["lote_id"])).sum()),
            "jaula": int((~hechos["jaula_id"].isin(jaulas["jaula_id"])).sum()),
            "centro": int((~hechos["centro_id"].isin(centros["centro_id"])).sum()),
            "especie": int((~hechos["especie"].isin(especies["especie"])).sum()),
        }
        return sum(huerfanos.values()) == 0, huerfanos

    def h03():
        excluidas = len(cosechas) - len(cosechas_validas)
        return excluidas / len(cosechas) <= 0.15, f"{excluidas} de {len(cosechas)} cosechas sin lote en el maestro"

    def h04():
        lotes_hechos = set(hechos["lote_id"])
        una = cosechas_validas.groupby("lote_id").size()
        sin = lotes_hechos - set(una.index)
        varias = sorted(una[una > 1].index)
        return not sin and not varias, f"{len(lotes_hechos) - len(sin)} de {len(lotes_hechos)} lotes con una cosecha válida" + (f"; con varias: {varias}" if varias else "")

    def h05():
        malos = {
            "alimento_kg < 0": int((hechos["alimento_kg"] < 0).sum()),
            "poblacion <= 0": int((hechos["poblacion"] <= 0).sum()),
            "biomasa_kg <= 0": int((hechos["biomasa_kg"] <= 0).sum()),
            "mortalidad fuera de [0, poblacion]": int(((hechos["mortalidad_n"] < 0) | (hechos["mortalidad_n"] > hechos["poblacion"])).sum()),
        }
        return sum(malos.values()) == 0, malos

    def h06():
        fuera = int(((hechos["fecha_dt"] < inicio) | (hechos["fecha_dt"] > fin)).sum())
        post = int((hechos["fecha_dt"] > hechos["fecha_cosecha"]).sum())
        excl = int(tabla_cobertura.query("motivo == 'posterior a la cosecha del lote'")["registros"].sum())
        return fuera == 0 and post == 0, f"{fuera} fuera del período y {post} post-cosecha en la tabla ({excl} excluidos en la limpieza)"

    def h07():
        corr = tabla_cobertura.query("fuente == 'operacion_diaria' and tipo == 'corregido'").set_index("motivo")["registros"]
        maximo = corr.max() / total_op
        return maximo <= 0.02, {m: int(v) for m, v in corr.items()}

    def h08():
        pct = float(comprobaciones.iloc[0]["pct_dias_que_calzan"])
        return pct >= 99, f"C1 calza en el {pct} % de los días"

    def h09():
        sin = int(hechos["costo_alimento_clp"].isna().sum())
        return sin == 0, f"{sin} jaulas-día sin precio"

    reg.registrar("H-01", "tabla de hechos", "modelo", "Unicidad de la clave del hecho: una fila por (lote, fecha)", BLOQUEA, "0 duplicados", h01)
    reg.registrar("H-02", "tabla de hechos", "modelo", "Sin huérfanos: lote, jaula, centro y especie existen en sus dimensiones", BLOQUEA, "0 huérfanos", h02)
    reg.registrar("H-03", "tabla de hechos", "SQLite", "Cosechas cuyo lote no existe: excluidas y dentro de lo esperado", AVISA, "≤ 15 %", h03)
    reg.registrar("H-04", "tabla de hechos", "modelo", "Cada lote tiene exactamente una cosecha válida (denominador de R)", BLOQUEA, "todos", h04)
    reg.registrar("H-05", "tabla de hechos", "modelo", "Rangos válidos de alimento, población, biomasa y mortalidad", BLOQUEA, "0 fuera de rango", h05)
    reg.registrar("H-06", "tabla de hechos", "modelo", "Fechas dentro del período y no posteriores a la cosecha del lote", BLOQUEA, "0 casos", h06)
    reg.registrar("H-07", "tabla de hechos", "SQLite", "Correcciones de digitación dentro de lo esperado (cada una ≤ 2 % de los registros)", AVISA, "≤ 2 %", h07)
    reg.registrar("H-08", "tabla de hechos", "SQLite", "Comprobación C1 de la población (sostiene la decisión 8)", AVISA, "≥ 99 %", h08)
    reg.registrar("H-09", "tabla de hechos", "modelo", "Toda jaula-día tiene precio del mes para pasar a pesos", BLOQUEA, "0 sin precio", h09)


# ---------------------------------------------------------------- métrica (capa de consumo)

def pruebas_metrica(reg, por_lote, por_centro, por_especie, brecha, tabla_cobertura, total_op, hechos,
                    sensibilidad, referencia, umbral_completitud):
    tol = 1e-6
    partes = ["cosecha", "evento", "basal"]

    def m01():
        peor = 0.0
        for t in [por_lote.assign(R=por_lote["alimento_kg"] / por_lote["denominador_kg"],
                                  **{f"R_{p}": por_lote[f"{p}_kg"] / por_lote["denominador_kg"] for p in partes}),
                  por_centro, por_especie]:
            peor = max(peor, float((t["R"] - t[[f"R_{p}" for p in partes]].sum(axis=1)).abs().max()))
        return peor < tol, f"diferencia máxima {peor:.2e}"

    def m02():
        dif = float((por_centro[[f"pct_{p}" for p in partes]].sum(axis=1) - 100).abs().max())
        return dif < tol, f"diferencia máxima {dif:.2e} puntos"

    def m03():
        negativos = int((por_lote[[f"{p}_kg" for p in partes]] < 0).sum().sum())
        return negativos == 0, f"{negativos} partes negativas"

    def m04():
        aporte = float(brecha.drop(index="total")["aporte_pct"].sum())
        dif_r = abs(float(brecha.drop(index="total")["brecha_R"].sum() - brecha.loc["total", "brecha_R"]))
        return abs(aporte - 100) < tol and dif_r < tol, f"aportes suman {aporte:.4f} %"

    def m05():
        partes_mm = brecha.drop(index="total")["sobrecosto_mm_clp"]
        total = float(brecha.loc["total", "sobrecosto_mm_clp"])
        texto = " + ".join(f"{v:.1f}" for v in partes_mm) + f" = {partes_mm.sum():.1f} (total {total:.1f}) millones CLP"
        return abs(partes_mm.sum() - total) < 1e-6, texto

    def m06():
        excl = int(tabla_cobertura.query("fuente == 'operacion_diaria' and tipo == 'excluido'")["registros"].sum())
        return 0 <= excl <= total_op, f"{excl} de {total_op} ({100 * excl / total_op:.2f} %)"

    def m07():
        excl = int(tabla_cobertura.query("fuente == 'operacion_diaria' and tipo == 'excluido'")["registros"].sum())
        pct = 100 * (total_op - excl) / total_op
        return pct >= umbral_completitud, f"{pct:.2f} % de los registros jaula-día recibidos entran a la tabla de hechos"

    def m09():
        excl = int(tabla_cobertura.query("fuente == 'operacion_diaria' and tipo == 'excluido'")["registros"].sum())
        return total_op == len(hechos) + excl, f"{total_op} leídos = {len(hechos)} en la tabla + {excl} excluidos"

    def m10():
        caro = por_centro["R"].idxmax()
        hoy = {"R_centro": float(por_centro.loc[caro, "R"]), "R_resto": float(brecha.loc["total", "R_resto"]),
               "aporte_cosecha": float(brecha.loc["cosecha", "aporte_pct"]),
               "aporte_evento": float(brecha.loc["evento", "aporte_pct"]),
               "aporte_basal": float(brecha.loc["basal", "aporte_pct"]),
               "sobrecosto_mm_clp": float(brecha.loc["total", "sobrecosto_mm_clp"])}
        difieren = {k: round(v, 3) for k, v in hoy.items() if abs(v - referencia[k][0]) > referencia[k][1]}
        return not difieren, "igual a la E1" if not difieren else f"cambió: {difieren}"

    def m11():
        centros = sorted(set(sensibilidad["centro_mas_caro"].astype(int)))
        return len(centros) == 1, f"centro más caro bajo las {len(sensibilidad)} definiciones: {centros}"

    reg.registrar("M-01", "métrica", "consumo", "R = R_cosecha + R_evento + R_basal por lote, centro y especie", BLOQUEA, "dif < 1e-6", m01)
    reg.registrar("M-02", "métrica", "consumo", "Las tres partes suman el 100 % del alimento", BLOQUEA, "dif < 1e-6", m02)
    reg.registrar("M-03", "métrica", "consumo", "Ninguna parte es negativa", BLOQUEA, "0", m03)
    reg.registrar("M-04", "métrica", "consumo", "La brecha se reparte sin residuo (aportes = 100 %)", BLOQUEA, "dif < 1e-6", m04)
    reg.registrar("M-05", "métrica", "consumo", "El sobrecosto en pesos de las 3 partes suma el total", BLOQUEA, "dif < 1e-6", m05)
    reg.registrar("M-06", "métrica", "consumo", "Cobertura: excluidos ÷ recibidos calculada desde el detalle", BLOQUEA, "0 ≤ excluidos ≤ recibidos", m06)
    reg.registrar("M-07", "métrica", "consumo", "Completitud contra el acuerdo de servicio", AVISA, f"≥ {umbral_completitud} %", m07)
    reg.registrar("M-09", "métrica", "consumo", "No se pierden registros: leídos = tabla de hechos + excluidos", BLOQUEA, "igualdad", m09)
    reg.registrar("M-10", "métrica", "consumo", "Las cifras principales coinciden con la E1 (si cambian, se explica)", AVISA, "tolerancia por cifra", m10)
    reg.registrar("M-11", "métrica", "consumo", "El centro más caro es el mismo bajo todas las definiciones alternativas", AVISA, "1 centro", m11)


def prueba_salidas(reg, cifras, carpeta):
    """M-08: lo que leen el informe y el prototipo (cifras.json y las tablas) es el mismo número."""
    def m08():
        por_centro = pd.read_csv(Path(carpeta) / "indicadores_por_centro.csv", index_col="centro_id")
        brecha = pd.read_csv(Path(carpeta) / "brecha_centro_caro.csv", index_col="parte")
        caro = cifras["centro_mas_caro"]["id"]
        pares = [(cifras["R"]["centro"], por_centro.loc[caro, "R"]),
                 (cifras["sobrecosto_mm_clp"]["total"], brecha.loc["total", "sobrecosto_mm_clp"])]
        dif = max(abs(a - b) for a, b in pares)
        return dif < 1e-6, f"diferencia máxima {dif:.1e} (cifras.json redondea a 6 decimales)"
    reg.registrar("M-08", "métrica", "consumo", "cifras.json y las tablas de results/ muestran el mismo número", BLOQUEA, "dif < 1e-6", m08)


def prueba_prototipo(reg, cifras, carpeta):
    """M-12: las tablas que lee el tablero (prototipo/datos/) muestran el mismo número que cifras.json, que es lo que
    cita el informe. Se evalúa sobre los archivos ya escritos en la carpeta de preparación, antes de reemplazar
    prototipo/datos/. Si falla, el tablero conserva la versión anterior (results/ ya quedó publicado y es válido)."""
    def m12():
        carpeta_ = Path(carpeta)
        meta = pd.read_csv(carpeta_ / "meta.csv").iloc[0]
        brecha = pd.read_csv(carpeta_ / "escenarios_brecha.csv")
        principal = brecha[brecha["escenario"] == "Principal"].set_index("orden_parte")
        rangos = cifras["rango_entre_definiciones"]
        pares = {
            "centro más caro": (cifras["centro_mas_caro"]["id"], meta["centro_caro_id"]),
            "R centro": (cifras["R"]["centro"], meta["R_centro_caro"]),
            "R resto": (cifras["R"]["resto"], meta["R_resto"]),
            "brecha R": (cifras["R"]["brecha"], meta["brecha_R"]),
            "sobrecosto total": (cifras["sobrecosto_mm_clp"]["total"], meta["sobrecosto_mm_clp"]),
            "cobertura %": (cifras["cobertura"]["pct_excluidos"], meta["cobertura_pct_excluido"]),
            "R mínimo": (rangos["R_centro"]["min"], meta["R_min_alternativas"]),
            "R máximo": (rangos["R_centro"]["max"], meta["R_max_alternativas"]),
            "sobrecosto mínimo": (rangos["sobrecosto_total_mm_clp"]["min"], meta["sobrecosto_min_mm_clp"]),
            "sobrecosto máximo": (rangos["sobrecosto_total_mm_clp"]["max"], meta["sobrecosto_max_mm_clp"]),
        }
        por_centro = pd.read_csv(carpeta_ / "escenarios_por_centro.csv")
        fila_caro = por_centro[(por_centro["escenario"] == "Principal") & (por_centro["es_centro_caro"] == 1)].iloc[0]
        pares["FCR bruto centro"] = (cifras["fcr_bruto_centro"], meta["fcr_bruto_centro_caro"])
        pares["FCR bruto resto"] = (cifras["fcr_bruto_resto"], meta["fcr_bruto_resto"])
        pares["FCR bruto centro (tabla por centro)"] = (cifras["fcr_bruto_centro"], fila_caro["R_bruto_gerencia"])
        for orden, parte in enumerate(["cosecha", "evento", "basal"], start=1):
            pares[f"aporte {parte}"] = (cifras["aporte_brecha_pct"][parte], principal.loc[orden, "aporte_pct"])
            pares[f"sobrecosto {parte}"] = (cifras["sobrecosto_mm_clp"][parte], principal.loc[orden, "sobrecosto_mm_clp"])
        dif = {k: abs(float(a) - float(b)) for k, (a, b) in pares.items()}
        peor = max(dif, key=dif.get)
        return dif[peor] < 1e-6, f"{len(pares)} cifras comparadas; diferencia máxima {dif[peor]:.1e} ({peor})"
    reg.registrar("M-12", "métrica", "prototipo", "El tablero (prototipo/datos/) muestra el mismo número que cifras.json; "
                  "si falla, no se actualiza el prototipo", BLOQUEA, "dif < 1e-6", m12)
