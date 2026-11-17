"""Capa de consumo del prototipo (Tableau) — AquaFiordo, Grupo 10 (S3).

Ejecuta, SIN modificarla, la lógica v3 de `entrega1.ipynb` y deja en `datos/` los CSV que lee
Tableau. La métrica se define una sola vez (el notebook / `salmonera`); este script sólo la
re-expresa en tablas para consumo. Cada vez que la cadena vuelve a correr, se vuelve a correr este
script y en Tableau basta con "Datos > Actualizar todos los extractos / orígenes".

Uso:
    python3 exportar_datos_tableau.py --repo "<ruta a Repo salmonera>"        # lee data/ del repo
Requisitos: pandas, numpy, matplotlib (los mismos del notebook). requests es opcional.

Si mindicador.cl no responde se usa data/cache/dolar.json; si tampoco existe, el prototipo declara
"dolar_origen = sin dato" y muestra todo en CLP (la métrica y los pesos no dependen del dólar).
"""
import argparse, json, os, shutil, sys, tempfile, datetime as dt
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True, help="carpeta del repo (con data/origen_*)")
ap.add_argument("--salida", default=str(Path(__file__).resolve().parent / "datos"))
args = ap.parse_args()
REPO, SALIDA = Path(args.repo).resolve(), Path(args.salida).resolve()
SALIDA.mkdir(parents=True, exist_ok=True)

# --- Copia de trabajo: el notebook escribe figuras/ al lado de data/, y no se toca el repo
TRABAJO = Path(tempfile.mkdtemp(prefix="salmonera_tableau_"))
shutil.copytree(REPO / "data", TRABAJO / "data", ignore=shutil.ignore_patterns(".git*"))
os.chdir(TRABAJO)

nb = json.load(open(REPO / "entrega1.ipynb", encoding="utf-8"))
celdas = [("".join(c["source"]), i) for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"]

ns = {"display": print, "__name__": "__notebook__"}
DOLAR_ORIGEN = "sin dato"
CACHE = REPO / "data" / "cache" / "dolar.json"

def cargar_dolar():
    """Celda 14 con la decisión de falla de la API: API -> caché -> sin dato (todo en CLP)."""
    global DOLAR_ORIGEN
    import requests
    filas = []
    try:
        for anio in (2025, 2026):
            r = requests.get(f"https://mindicador.cl/api/dolar/{anio}", timeout=20)
            r.raise_for_status()
            filas.extend(r.json()["serie"])
        DOLAR_ORIGEN = "mindicador.cl (en vivo)"
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(filas), encoding="utf-8")
    except Exception as e:
        print(f"AVISO: mindicador.cl no responde ({type(e).__name__}).", file=sys.stderr)
        if CACHE.exists():
            filas = json.loads(CACHE.read_text(encoding="utf-8"))
            DOLAR_ORIGEN = "caché data/cache/dolar.json"
        else:
            DOLAR_ORIGEN = "sin dato (API caída y sin caché): el prototipo muestra sólo CLP"
    df = pd.DataFrame(filas, columns=["fecha", "valor"]) if filas else pd.DataFrame({"fecha": pd.Series(dtype=str), "valor": pd.Series(dtype=float)})
    return df

for src, i in celdas:
    if "%pip" in src:
        continue
    if i == 14:
        ns["dolar"] = cargar_dolar()
        continue
    exec(compile(src, f"<celda {i}>", "exec"), ns)

g = ns  # atajo
DEC, centros, nombre_centro, jaulas = g["DECISIONES"], g["centros"], g["nombre_centro"], g["jaulas"]
CLAVES_PARTES = {"cosecha": "Eficiencia (peces cosechados)", "evento": "Evento sanitario", "basal": "Mortalidad normal (basal)"}
ahora = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
PALANCA = {"cosecha": "Protocolo de alimentación", "evento": "Sanidad (detección y tratamiento)", "basal": "Esperable: sin acción"}

def corrida(dec):
    hechos = g["construir_hechos"](dec)
    final = g["separar_muertes"](g["cruzar_con_eventos"](hechos, g["ventanas_de_eventos"](dec)), dec)
    por_centro = g["agregar"](g["tabla_por_lote"](final, dec), ["centro_id"])
    caro = por_centro["R"].idxmax()
    brecha = g["brecha_centro_caro"](por_centro, caro)
    return final, por_centro, caro, brecha

ESCENARIOS = g["ALTERNATIVAS"]  # Principal + decisiones 1..9
ESC_CORTO = {k: ("Principal" if k == "Principal" else k) for k in ESCENARIOS}

# ---------------------------------------------------------------- tablas por escenario
filas_centro, filas_brecha, filas_esc = [], [], []
for nombre, cambio in ESCENARIOS.items():
    dec = {**DEC, **cambio}
    final, por_centro, caro, brecha = corrida(dec)
    ref = final[final["en_ventana"] == 0]
    for cid, r in por_centro.iterrows():
        for parte, etiqueta in CLAVES_PARTES.items():
            filas_centro.append({
                "escenario": nombre, "centro_id": cid, "centro": nombre_centro[cid], "es_centro_caro": int(cid == caro),
                "parte": etiqueta, "orden_parte": list(CLAVES_PARTES).index(parte) + 1, "palanca": PALANCA[parte],
                "R_parte": r[f"R_{parte}"], "pct_del_alimento": r[f"pct_{parte}"],
                "clp_por_kg": r[f"clp_por_kg_{parte}"], "mm_clp": r[f"{parte}_clp"] / 1e6,
                "R_total": r["R"], "R_bruto_gerencia": r["R_bruto_gerencia"],
                "alimento_kg": r["alimento_kg"], "kg_cosechados": r["kg_cosechados"], "denominador_kg": r["denominador_kg"],
            })
    for parte, etiqueta in list(CLAVES_PARTES.items()) + [("total", "Total")]:
        b = brecha.loc[parte]
        filas_brecha.append({
            "escenario": nombre, "centro_caro_id": caro, "centro_caro": nombre_centro[caro],
            "parte": etiqueta, "orden_parte": (list(CLAVES_PARTES).index(parte) + 1) if parte != "total" else 4,
            "palanca": PALANCA.get(parte, "Total"),
            "R_centro_caro": b["R_centro_caro"], "R_resto": b["R_resto"], "brecha_R": b["brecha_R"],
            "aporte_pct": b["aporte_pct"], "sobrecosto_mm_clp": b["sobrecosto_mm_clp"],
        })
    filas_esc.append({
        "escenario": nombre, "es_principal": int(nombre == "Principal"), "centro_caro_id": caro,
        "R_centro_caro": brecha.loc["total", "R_centro_caro"], "R_resto": brecha.loc["total", "R_resto"],
        "brecha_R": brecha.loc["total", "brecha_R"], "sobrecosto_total_mm_clp": brecha.loc["total", "sobrecosto_mm_clp"],
        "aporte_eficiencia_pct": brecha.loc["cosecha", "aporte_pct"], "aporte_evento_pct": brecha.loc["evento", "aporte_pct"],
        "aporte_basal_pct": brecha.loc["basal", "aporte_pct"],
        "basal_por_10mil": 10000 * ref["mortalidad_n"].sum() / ref["pob0"].sum(),
        "alimento_perdido_evento_ton": por_centro["evento_kg"].sum() / 1000,
    })
    if nombre == "Principal":
        final_principal, centro_principal, CARO, brecha_principal = final, por_centro, caro, brecha

df_centro, df_brecha, df_esc = map(pd.DataFrame, (filas_centro, filas_brecha, filas_esc))
base = df_esc.set_index("escenario").loc["Principal"]
df_esc["cambio_pct_R_centro"] = 100 * (df_esc["R_centro_caro"] / base["R_centro_caro"] - 1)
df_esc["cambio_pct_brecha"] = 100 * (df_esc["brecha_R"] / base["brecha_R"] - 1)
df_esc["es_denominador"] = df_esc["escenario"].isin(["Principal", "1 · denominador: biomasa ganada"]).astype(int)
df_esc["es_basal"] = df_esc["escenario"].isin(["Principal", "4 · basal por etapa del ciclo"]).astype(int)

# ---------------------------------------------------------------- hechos (grano: una jaula en un día)
f = final_principal.copy()
f["centro"] = f["centro_id"].map(nombre_centro)
hechos = f.assign(fecha=f["fecha_dt"].dt.strftime("%Y-%m-%d"), fecha_cosecha=f["fecha_cosecha"].dt.strftime("%Y-%m-%d"))[[
    "fecha", "centro_id", "centro", "jaula_id", "lote_id", "especie", "pob0", "mortalidad_n", "m_basal", "m_evento",
    "alimento_kg", "biomasa_kg", "peso_promedio_kg", "acumulado_por_pez_kg", "perdido_basal_kg", "perdido_evento_kg",
    "costo_alimento_clp", "perdido_basal_clp", "perdido_evento_clp", "en_ventana", "evento_id", "tipo_evento",
    "jaula_listada", "fecha_cosecha"]]

# ---------------------------------------------------------------- eventos y las dos fuentes de mortalidad
conc = g["conciliar_eventos"](final_principal).copy()
conc["centro"] = conc["centro_id"].map(nombre_centro)
conc["brecha_declarada_vs_centro"] = conc["declarada_sanidad"] - conc["diaria_centro_completo"]
def lectura(r):
    if abs(r["diaria_centro_completo"] - r["declarada_sanidad"]) <= 0.05 * r["declarada_sanidad"]:
        return "Calzan: la operación diaria del centro completo reproduce lo declarado (las jaulas listadas solas no)."
    return "No concilian: lo declarado por sanidad no aparece como alza sobre la basal en la operación diaria (dos registros de áreas distintas)."
conc["lectura"] = conc.apply(lectura, axis=1)
fuentes_long = conc.melt(
    id_vars=["evento_id", "tipo", "centro_id", "centro"],
    value_vars=["declarada_sanidad", "diaria_jaulas_listadas", "diaria_centro_completo"],
    var_name="fuente", value_name="muertes").replace({"fuente": {
        "declarada_sanidad": "1 · Declarada por sanidad", "diaria_jaulas_listadas": "2 · Operación diaria, jaulas listadas",
        "diaria_centro_completo": "3 · Operación diaria, centro completo"}})

# ---------------------------------------------------------------- cobertura
cob = g["tabla_cobertura"].copy()
op_total = int(cob.query("fuente == 'operacion_diaria'")["total"].iloc[0])
excl = int(cob.query("fuente == 'operacion_diaria' and tipo == 'excluido'")["registros"].sum())
COB_PCT = 100 * excl / op_total

# ---------------------------------------------------------------- pruebas de calidad (semilla de B3)
pruebas = []
def prueba(fuente, nombre, que_verifica, si_falla, ok, detalle=""):
    pruebas.append({"fuente": fuente, "prueba": nombre, "que_verifica": que_verifica, "si_falla": si_falla,
                    "resultado": "OK" if ok else "FALLA", "detalle": detalle})
fp = final_principal
prueba("operacion_diaria (SQLite)", "unicidad_clave_hecho", "(jaula_id, fecha) no se repite en la tabla de hechos", "bloquea la carga",
       not fp.duplicated(["jaula_id", "fecha_dt"]).any())
prueba("operacion_diaria (SQLite)", "sin_huerfanos_dimensiones", "todo hecho tiene centro y especie", "bloquea la carga",
       fp["centro_id"].notna().all() and fp["especie"].notna().all())
prueba("operacion_diaria (SQLite)", "rangos_validos", "0 <= mortalidad_n <= población y alimento_kg > 0", "bloquea la carga",
       bool(((fp["mortalidad_n"] >= 0) & (fp["mortalidad_n"] <= fp["pob0"]) & (fp["alimento_kg"] > 0)).all()))
prueba("operacion_diaria (SQLite)", "fechas_en_periodo", "cada fecha cae entre la 1.ª fecha y la cosecha de su lote", "bloquea la carga",
       bool((fp["fecha_dt"] <= fp["fecha_cosecha"]).all()), f"{fp['fecha_dt'].min():%Y-%m-%d} a {fp['fecha_dt'].max():%Y-%m-%d}")
prueba("costos_alimento (CSV)", "precio_valido", "todo mes con hechos tiene precio de alimento (>0)", "avisa",
       bool(fp["costo_alimento_clp"].notna().all() and (fp["costo_alimento_clp"] > 0).all()))
prueba("eventos_sanitarios (JSON)", "eventos_con_centro_valido", "todo evento usado pertenece a un centro de la base", "avisa (los excluidos quedan en cobertura)",
       bool(g["eventos_jaulas"]["centro_id"].isin(centros["centro_id"]).all()))
dolar_ok = not DOLAR_ORIGEN.startswith("sin dato")
prueba("mindicador.cl (API)", "api_responde_o_cache", "hay dólar en vivo o en caché", "avisa: el prototipo muestra sólo CLP", dolar_ok, DOLAR_ORIGEN)
suma_R = (df_centro[df_centro["escenario"] == "Principal"].groupby("centro_id").agg(s=("R_parte", "sum"), t=("R_total", "first")))
prueba("métrica", "partes_suman_R", "R_cosecha + R_evento + R_basal = R en cada centro", "bloquea la carga", bool(np.allclose(suma_R["s"], suma_R["t"])))
bp = df_brecha[(df_brecha["escenario"] == "Principal") & (df_brecha["parte"] != "Total")]
prueba("métrica", "reparto_suma_100", "los aportes de las tres partes a la brecha suman 100 %", "bloquea la carga", bool(abs(bp["aporte_pct"].sum() - 100) < 1e-6))
df_pruebas = pd.DataFrame(pruebas)
n_ok, n_tot = int((df_pruebas["resultado"] == "OK").sum()), len(df_pruebas)

# ---------------------------------------------------------------- metadatos (pie de la pantalla) y cifras de referencia
rng = lambda c: (df_esc[c].min(), df_esc[c].max())
coma = lambda v: f"{v:.2f}".replace(".", ",")   # coma decimal en los textos, como en los ejes de Tableau
periodo_desde, periodo_hasta = hechos["fecha"].min(), hechos["fecha"].max()
meta = pd.DataFrame([{
    "fecha_actualizacion": ahora, "periodo_desde": periodo_desde, "periodo_hasta": periodo_hasta,
    "fuentes": "origen_acuicultura.sqlite · origen_costos_alimento.csv · origen_eventos_sanitarios.json · mindicador.cl",
    "dueno_del_dato": "Gerencia de Operaciones de AquaFiordo (cargo por confirmar con la contraparte)",
    "definiciones_certificadas_por": "Grupo 10 (S3), ficha de la métrica v3; validación de la contraparte: pendiente",
    "dolar_origen": DOLAR_ORIGEN,
    "cobertura_pct_excluido": COB_PCT, "registros_excluidos": excl, "registros_totales": op_total,
    "pruebas_ok": n_ok, "pruebas_total": n_tot,
    "centro_caro": nombre_centro[CARO], "centro_caro_id": CARO,
    "R_centro_caro": base["R_centro_caro"], "R_resto": base["R_resto"], "brecha_R": base["brecha_R"],
    "R_min_alternativas": rng("R_centro_caro")[0], "R_max_alternativas": rng("R_centro_caro")[1],
    "sobrecosto_mm_clp": base["sobrecosto_total_mm_clp"],
    "sobrecosto_min_mm_clp": rng("sobrecosto_total_mm_clp")[0], "sobrecosto_max_mm_clp": rng("sobrecosto_total_mm_clp")[1],
    "aporte_evento_min_pct": rng("aporte_evento_pct")[0], "aporte_evento_max_pct": rng("aporte_evento_pct")[1],
    "aporte_eficiencia_min_pct": rng("aporte_eficiencia_pct")[0], "aporte_eficiencia_max_pct": rng("aporte_eficiencia_pct")[1],
    "sla_frescura": "semanal (cada lunes, tras la corrida de la cadena)", "sla_completitud_min_pct": 98, "sla_calidad_min_pct": 100,
}])

meta["texto_pie"] = (
    "Fuente: origen_acuicultura.sqlite, origen_costos_alimento.csv, origen_eventos_sanitarios.json y mindicador.cl · "
    f"Actualizado: {ahora} · Dueño del dato: {meta['dueno_del_dato'].iloc[0]} · "
    f"Cobertura: {coma(COB_PCT)} % de los registros jaula-día excluido ({excl} de {op_total}) · "
    f"Pruebas de calidad: {n_ok}/{n_tot} en verde · Definiciones: {meta['definiciones_certificadas_por'].iloc[0]}")

meta["texto_referencia"] = (
    f"Referencia ({nombre_centro[CARO]}, definición principal): el evento sanitario explica {base['aporte_evento_pct']:.0f} % del sobrecosto "
    f"(rango entre definiciones: {rng('aporte_evento_pct')[0]:.0f}–{rng('aporte_evento_pct')[1]:.0f} %); "
    f"la eficiencia explica {base['aporte_eficiencia_pct']:.0f} % (rango {rng('aporte_eficiencia_pct')[0]:.0f}–{rng('aporte_eficiencia_pct')[1]:.0f} %). "
    f"R = {coma(base['R_centro_caro'])} kg/kg (rango {coma(rng('R_centro_caro')[0])}–{coma(rng('R_centro_caro')[1])}).")

# ---------------------------------------------------------------- escribir
def guardar(df, nombre):
    df.to_csv(SALIDA / nombre, index=False, encoding="utf-8", float_format="%.6g" if False else None)
guardar(hechos, "hechos_jaula_dia.csv")
guardar(df_centro, "escenarios_por_centro.csv")
guardar(df_brecha, "escenarios_brecha.csv")
guardar(df_esc, "escenarios_resumen.csv")
guardar(conc, "eventos_conciliacion.csv")
guardar(fuentes_long, "eventos_fuentes_mortalidad.csv")
guardar(g["en_torno"].assign(fecha=g["en_torno"]["fecha_dt"].dt.strftime("%Y-%m-%d")).drop(columns=["fecha_dt"]), "mortalidad_en_torno_a_eventos.csv")
guardar(cob, "cobertura.csv")
guardar(df_pruebas, "pruebas_calidad.csv")
guardar(meta, "meta.csv")

print(f"\nListo: {len(hechos):,} hechos, {len(df_esc)} escenarios -> {SALIDA}")
print(f"Centro más caro: {nombre_centro[CARO]} · R = {base['R_centro_caro']:.3f} (resto {base['R_resto']:.3f}); brecha {base['brecha_R']:.3f}")
print(f"Reparto: {base['aporte_eficiencia_pct']:.1f} / {base['aporte_evento_pct']:.1f} / {base['aporte_basal_pct']:.1f} %  · sobrecosto {base['sobrecosto_total_mm_clp']:.0f} MM CLP")
print(f"Cobertura excluida: {COB_PCT:.2f} %  · pruebas {n_ok}/{n_tot} OK · dólar: {DOLAR_ORIGEN}")
