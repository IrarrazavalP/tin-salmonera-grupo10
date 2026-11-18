"""
metrica.py — Capa semántica (componente C) · Grupo 10 · Salmonera · IIC3752

La métrica queda definida una sola vez aquí. El notebook (entrega2.ipynb) la importa; el informe y el
prototipo leen lo que el notebook escribe con ella en results/ y prototipo/datos/.

    R = kg de alimento ÷ kg cosechados = R_cosecha + R_evento + R_basal
    R_bruto_gerencia (FCR bruto) = alimento ÷ biomasa final: el indicador que se reporta al directorio

Contenido: las fórmulas F5 a F15 del plan de la Entrega 1 (v3), movidas desde las celdas 37, 39, 41, 43, 46,
50 y 51 del notebook sin reescribirlas, y la regla del 5 % para la conciliación de las dos fuentes de
mortalidad, que vivía en la celda del prototipo (regla pendiente C6).

Lo único que cambió al moverlas: las funciones leían cuatro variables globales del notebook
(eventos_jaulas, cosechas_validas, DOLAR_PERIODO y, en correr/corrida_con, los pasos de la capa 3). Ahora el
notebook se las entrega una vez con configurar(...) y los nombres y firmas de las funciones son los mismos.

Uso en el notebook (antes de la sección 6):

    import metrica
    importlib.reload(metrica)
    from metrica import (DECISIONES, ALTERNATIVAS, PARTES, SUMAS, TOLERANCIA_FUENTES, basal_global, tasa_basal,
                         separar_muertes, conciliar_eventos, lectura_fuentes, tabla_por_lote, indicadores, agregar,
                         brecha_centro_caro, correr, corrida_con)
    metrica.configurar(eventos_jaulas=eventos_jaulas, cosechas_validas=cosechas_validas,
                       dolar_periodo=DOLAR_PERIODO,
                       preparar=lambda dec: cruzar_con_eventos(construir_hechos(dec), ventanas_de_eventos(dec)))
"""

import pandas as pd

# ---------------------------------------------------------------------------------------------------------
# Decisiones de definición (sección 3 del plan). Principal y alternativas: la métrica recibe la decisión
# como parámetro (dec) y el prototipo muestra las alternativas como medidas seleccionables (C4).
# ---------------------------------------------------------------------------------------------------------
DECISIONES = {
    "denominador": "cosechado",   # 1. "cosechado" o "ganada"
    "precio": "mensual",          # 2. "mensual" o "por_peso"
    "perdido": "acumulado",       # 3. "acumulado" o "peso_fcr"
    "basal": "global",            # 4. "global" o "etapa"
    "dias_previos": 0,            # 5. N: días que la ventana se adelanta a la fecha declarada (se fija en la sección 5)
    "sin_jaulas": "centro",       # 6. "centro" o "excluir"
    "mortalidad": "diaria",       # 7. "diaria" o "sanidad"
    "lectura": "antes",           # 8. población registrada "antes" o "despues" de descontar los muertos del día
    "alcance": "centro",          # 9. "centro" o "declaradas"
}

ALTERNATIVAS = {
    "Principal": {},
    "1 · denominador: biomasa ganada": {"denominador": "ganada"},
    "2 · precio según el peso del pez": {"precio": "por_peso"},
    "3 · perdido = peso promedio x FCR": {"perdido": "peso_fcr"},
    "4 · basal por etapa del ciclo": {"basal": "etapa"},
    "5 · ventana desde 7 días antes": {"dias_previos": 7},
    "6 · excluir eventos sin jaulas": {"sin_jaulas": "excluir"},
    "7 · mortalidad declarada por sanidad": {"mortalidad": "sanidad"},
    "8 · población ya sin los muertos del día": {"lectura": "despues"},
    "9 · sólo las jaulas que lista sanidad": {"alcance": "declaradas"},
}

PARTES = ["cosecha", "evento", "basal"]

SUMAS = ["alimento_kg", "costo_clp", "denominador_kg", "kg_cosechados", "biomasa_final_kg", "m_basal", "m_evento",
         "cosecha_kg", "evento_kg", "basal_kg", "cosecha_clp", "evento_clp", "basal_clp"]

# Regla del 5 % (C6): las dos fuentes de mortalidad «calzan» si la operación diaria del centro completo
# difiere de lo que declara sanidad en a lo más 5 % de lo declarado. Nació en la celda del prototipo.
TOLERANCIA_FUENTES = 0.05


# ---------------------------------------------------------------------------------------------------------
# Entradas que vienen de las capas 1 a 3 del notebook (antes eran variables globales)
# ---------------------------------------------------------------------------------------------------------
_CONTEXTO = {}


def configurar(eventos_jaulas, cosechas_validas, dolar_periodo, preparar=None):
    """Entrega a la capa semántica las tablas de las capas anteriores.

    eventos_jaulas: eventos depurados (celda 12), con jaulas_afectadas y mortalidad_asociada.
    cosechas_validas: cosechas de lotes del maestro, con kilos_vivos y fecha_cosecha (celda 20).
    dolar_periodo: dólar promedio del período (celda 26); NaN si no hay API ni copia guardada.
    preparar: función dec -> tabla jaula-día cruzada con las ventanas de los eventos (capa 3).
              Solo la usan correr y corrida_con.
    """
    _CONTEXTO.update(eventos_jaulas=eventos_jaulas, cosechas_validas=cosechas_validas,
                     dolar_periodo=dolar_periodo, preparar=preparar)


def _ctx(nombre):
    if _CONTEXTO.get(nombre) is None:
        raise RuntimeError(f"metrica: falta «{nombre}». Llama a metrica.configurar(...) antes de usar la métrica.")
    return _CONTEXTO[nombre]


# ---------------------------------------------------------------------------------------------------------
# F5 · Mortalidad basal (decisión 4)
# ---------------------------------------------------------------------------------------------------------
def basal_global(cruzada):
    """F5 global: Σ mortalidad_n ÷ Σ pob0 en las jaulas-día fuera de la ventana de todo evento."""
    referencia = cruzada[cruzada["en_ventana"] == 0]
    return referencia["mortalidad_n"].sum() / referencia["pob0"].sum()


def tasa_basal(cruzada, dec):
    """F5: agrega la columna tasa_basal a cada jaula-día, al nivel que indica la decisión 4."""
    referencia = cruzada[cruzada["en_ventana"] == 0]
    tasa_global = referencia["mortalidad_n"].sum() / referencia["pob0"].sum()
    if dec["basal"] == "global":
        return cruzada.assign(tasa_basal=tasa_global)
    sumas = referencia.groupby("etapa_peso")[["mortalidad_n", "pob0"]].sum()
    por_etapa = (sumas["mortalidad_n"] / sumas["pob0"]).rename("tasa_basal").reset_index()
    f = cruzada.merge(por_etapa, on="etapa_peso", how="left")
    f["tasa_basal"] = f["tasa_basal"].fillna(tasa_global)
    return f


# ---------------------------------------------------------------------------------------------------------
# F6 a F8 · Muertes basales y de evento, y alimento perdido (decisión 7)
# ---------------------------------------------------------------------------------------------------------
def separar_muertes(cruzada, dec):
    eventos_jaulas = _ctx("eventos_jaulas")
    f = tasa_basal(cruzada, dec)
    esperadas = f["tasa_basal"] * f["pob0"]

    if dec["mortalidad"] == "diaria":
        # F6: en ventana, las muertes basales son a lo más lo que predice la basal
        f["m_basal"] = f["mortalidad_n"].where(f["en_ventana"] == 0, pd.concat([f["mortalidad_n"], esperadas], axis=1).min(axis=1))
    else:
        # Alternativa: las muertes del evento son las que declara sanidad, repartidas entre los
        # días de la ventana en proporción a la mortalidad diaria (con tope en ella)
        declarada = f["evento_id"].map(eventos_jaulas.set_index("evento_id")["mortalidad_asociada"].astype(float))
        en_ventana = f.groupby("evento_id")["mortalidad_n"].transform("sum")
        parte = (declarada / en_ventana).fillna(0).clip(upper=1)
        f["m_basal"] = f["mortalidad_n"] * (1 - parte)

    f["m_evento"] = f["mortalidad_n"] - f["m_basal"]   # F7

    # F8 (y su versión en pesos, F14): alimento que ya se habían comido los peces que murieron
    for unidad in ["kg", "clp"]:
        f[f"perdido_basal_{unidad}"] = f["m_basal"] * f[f"acumulado_por_pez_{unidad}"]
        f[f"perdido_evento_{unidad}"] = f["m_evento"] * f[f"acumulado_por_pez_{unidad}"]
    return f


# ---------------------------------------------------------------------------------------------------------
# Conciliación con la mortalidad que declara sanidad, y regla del 5 % (C6)
# ---------------------------------------------------------------------------------------------------------
def conciliar_eventos(final):
    eventos_jaulas = _ctx("eventos_jaulas")
    filas = []
    for ev in eventos_jaulas.itertuples():
        inicio = pd.to_datetime(ev.fecha_inicio, format="%d/%m/%Y")
        fin = pd.to_datetime(ev.fecha_fin, format="%d/%m/%Y")
        periodo = final[(final["fecha_dt"] >= inicio) & (final["fecha_dt"] <= fin) & (final["centro_id"] == ev.centro_id)]
        del_evento = final[final["evento_id"] == ev.evento_id]
        muertes = del_evento["m_evento"].sum()
        filas.append({
            "evento_id": ev.evento_id, "tipo": ev.tipo, "centro_id": ev.centro_id,
            "declarada_sanidad": int(ev.mortalidad_asociada),
            "diaria_jaulas_listadas": periodo[periodo["jaula_id"].isin(ev.jaulas_afectadas)]["mortalidad_n"].sum(),
            "diaria_centro_completo": periodo["mortalidad_n"].sum(),
            "muertes_de_evento": muertes,
            "alimento_perdido_kg": del_evento["perdido_evento_kg"].sum(),
            "alimento_perdido_mm_clp": del_evento["perdido_evento_clp"].sum() / 1e6,
            "alimento_por_pez_muerto_kg": del_evento["perdido_evento_kg"].sum() / muertes if muertes else float("nan"),
            "dias_a_cosecha_promedio": (del_evento["fecha_cosecha"] - del_evento["fecha_dt"]).dt.days.mean(),
        })
    return pd.DataFrame(filas)


def calzan(declarada, diaria, tolerancia=TOLERANCIA_FUENTES):
    """Regla del 5 %: |diaria − declarada| ≤ tolerancia × declarada (la base es lo que declara sanidad)."""
    return abs(diaria - declarada) <= tolerancia * declarada


def lectura_fuentes(r):
    """Lectura de un evento de la conciliación (una fila de conciliar_eventos) para el prototipo."""
    if calzan(r["declarada_sanidad"], r["diaria_centro_completo"]):
        return "Calzan: la operación diaria del centro completo reproduce lo declarado (las jaulas listadas solas no)."
    return ("No concilian: lo declarado por sanidad no aparece como alza sobre la basal en la operación diaria "
            "(dos registros de áreas distintas).")


# ---------------------------------------------------------------------------------------------------------
# F9 a F12 · R y sus tres partes (decisión 1), FCR bruto y pesos (F14)
# ---------------------------------------------------------------------------------------------------------
def tabla_por_lote(final, dec):
    cosechas_validas = _ctx("cosechas_validas")
    lote = final.groupby(["centro_id", "especie", "lote_id"], as_index=False).agg(
        alimento_kg=("alimento_kg", "sum"), costo_clp=("costo_alimento_clp", "sum"),
        biomasa_inicial_kg=("biomasa_kg", "first"), biomasa_final_kg=("biomasa_kg", "last"),
        m_basal=("m_basal", "sum"), m_evento=("m_evento", "sum"),
        basal_kg=("perdido_basal_kg", "sum"), evento_kg=("perdido_evento_kg", "sum"),
        basal_clp=("perdido_basal_clp", "sum"), evento_clp=("perdido_evento_clp", "sum"),
    )
    lote = lote.merge(cosechas_validas[["lote_id", "kilos_vivos"]].rename(columns={"kilos_vivos": "kg_cosechados"}), on="lote_id")
    # F9: lo que no se perdió en peces muertos es lo que comieron los peces cosechados
    lote["cosecha_kg"] = lote["alimento_kg"] - lote["basal_kg"] - lote["evento_kg"]
    lote["cosecha_clp"] = lote["costo_clp"] - lote["basal_clp"] - lote["evento_clp"]
    # Decisión 1: denominador
    if dec["denominador"] == "cosechado":
        lote["denominador_kg"] = lote["kg_cosechados"]
    else:   # biomasa ganada: cosechada − biomasa del lote en su primer registro
        lote["denominador_kg"] = lote["kg_cosechados"] - lote["biomasa_inicial_kg"]
    return lote


def indicadores(sumas):
    """F10, F11 y F14 sobre una tabla que ya trae sumados numeradores y denominadores."""
    DOLAR_PERIODO = _CONTEXTO.get("dolar_periodo", float("nan"))
    g = sumas.copy()
    g["R"] = g["alimento_kg"] / g["denominador_kg"]
    for parte in ["cosecha", "evento", "basal"]:
        g[f"R_{parte}"] = g[f"{parte}_kg"] / g["denominador_kg"]
        g[f"pct_{parte}"] = 100 * g[f"{parte}_kg"] / g["alimento_kg"]
        g[f"clp_por_kg_{parte}"] = g[f"{parte}_clp"] / g["denominador_kg"]
    g["clp_por_kg"] = g["costo_clp"] / g["denominador_kg"]
    g["usd_por_kg"] = g["clp_por_kg"] / DOLAR_PERIODO
    g["R_bruto_gerencia"] = g["alimento_kg"] / g["biomasa_final_kg"]
    return g


def agregar(por_lote, por):
    """F12: suma los lotes y recién entonces divide."""
    sumas = por_lote.groupby(por)[SUMAS].sum()
    sumas.insert(0, "lotes", por_lote.groupby(por).size())
    return indicadores(sumas)


def indicadores_resto(por_centro, caro):
    """F12 sobre todos los centros menos el más caro (el «resto» de F13)."""
    return indicadores(por_centro.drop(index=caro)[SUMAS].sum().to_frame().T).iloc[0]


# ---------------------------------------------------------------------------------------------------------
# F13 y F14 · Brecha del centro con más costo y sobrecosto en pesos
# ---------------------------------------------------------------------------------------------------------
def brecha_centro_caro(por_centro, caro):
    resto = indicadores(por_centro.drop(index=caro)[SUMAS].sum().to_frame().T).iloc[0]
    centro = por_centro.loc[caro]
    filas = []
    for parte, sufijo in [("cosecha", "_cosecha"), ("evento", "_evento"), ("basal", "_basal"), ("total", "")]:
        filas.append({
            "parte": parte,
            "R_centro_caro": centro[f"R{sufijo}"], "R_resto": resto[f"R{sufijo}"],
            "brecha_R": centro[f"R{sufijo}"] - resto[f"R{sufijo}"],
            "brecha_clp_por_kg": centro[f"clp_por_kg{sufijo}"] - resto[f"clp_por_kg{sufijo}"],
        })
    b = pd.DataFrame(filas).set_index("parte")
    b["aporte_pct"] = 100 * b["brecha_R"] / b.loc["total", "brecha_R"]
    # F14: lo que el centro gastó de más en alimento por no rendir como el resto
    b["sobrecosto_mm_clp"] = b["brecha_clp_por_kg"] * centro["denominador_kg"] / 1e6
    return b


# ---------------------------------------------------------------------------------------------------------
# F15 · Sensibilidad y alternativas (C4)
# ---------------------------------------------------------------------------------------------------------
def correr(dec):
    """Corre el análisis completo con un juego de decisiones y devuelve las cifras que se comparan."""
    final = separar_muertes(_ctx("preparar")(dec), dec)
    centro = agregar(tabla_por_lote(final, dec), ["centro_id"])
    caro = centro["R"].idxmax()
    b = brecha_centro_caro(centro, caro)
    referencia = final[final["en_ventana"] == 0]
    return {
        "centro_mas_caro": caro,
        "R_centro": centro.loc[caro, "R"], "R_resto": b.loc["total", "R_resto"], "brecha_R": b.loc["total", "brecha_R"],
        "pct_cosecha": centro.loc[caro, "pct_cosecha"], "pct_evento": centro.loc[caro, "pct_evento"],
        "pct_basal": centro.loc[caro, "pct_basal"],
        "aporte_cosecha": b.loc["cosecha", "aporte_pct"], "aporte_evento": b.loc["evento", "aporte_pct"],
        "aporte_basal": b.loc["basal", "aporte_pct"],
        "clp_por_kg_centro": centro.loc[caro, "clp_por_kg"],
        "perdido_evento_ton": centro["evento_kg"].sum() / 1000,
        "basal_por_10000": 10000 * referencia["mortalidad_n"].sum() / referencia["pob0"].sum(),
    }


def corrida_con(dec):
    """Tabla final jaula-día e indicadores por centro bajo un juego de decisiones."""
    final = separar_muertes(_ctx("preparar")(dec), dec)
    return final, agregar(tabla_por_lote(final, dec), ["centro_id"])
