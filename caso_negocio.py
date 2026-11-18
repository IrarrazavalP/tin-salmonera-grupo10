"""Cifras del caso de negocio (sección E): valor, costo y margen de cada palanca.

Lee lo que escribe entrega2.ipynb en results/ y deja results/caso_negocio.json.
Los costos, la meta y la fracción evitable son los que dio la contraparte (no salen de los datos del caso).
Uso: python caso_negocio.py   (después de correr entrega2.ipynb)
"""
import json
from pathlib import Path

import pandas as pd

RESULTS = Path("results")

# Respuesta de la contraparte (verbalizado)
COSTO_AUDITORIA_MM = (20, 25)        # CLP millones, una vez, + ~150 h de personal propio en 2 meses
HORAS_AUDITORIA = 150
COSTO_SANIDAD_MM = (60, 80)          # CLP millones por ciclo
EVITABLE_BROTE = (0.30, 0.40)        # fracción del efecto del brote evitable con detección temprana
META_PRIMER_CICLO = 0.5              # cerrar la mitad de la brecha de eficiencia en el primer ciclo; el resto en el segundo
HORAS_PLANILLA_MES = (12, 15)        # planilla Excel del FCR bruto que reemplaza el prototipo


def main():
    cifras = json.loads((RESULTS / "cifras.json").read_text(encoding="utf-8"))
    caro = cifras["centro_mas_caro"]["id"]
    s = cifras["sobrecosto_mm_clp"]
    centro = pd.read_csv(RESULTS / "indicadores_por_centro.csv").set_index("centro_id").loc[caro]
    hechos = pd.read_csv(RESULTS / "hechos_jaula_dia.csv", usecols=[
        "lote_id", "centro_id", "fecha_dt", "alimento_kg", "poblacion_comio", "acumulado_por_pez_kg"])

    # Alimento que había comido un pez al llegar a la cosecha (día de cosecha incluido), ponderado por peces cosechados
    ultimo = hechos[hechos["centro_id"] == caro].sort_values("fecha_dt").groupby("lote_id").tail(1)
    por_pez = ultimo["acumulado_por_pez_kg"] + ultimo["alimento_kg"] / ultimo["poblacion_comio"]
    kg_por_pez_cosechado = (por_pez * ultimo["poblacion_comio"]).sum() / ultimo["poblacion_comio"].sum()
    eventos = pd.read_csv(RESULTS / "eventos_sanitarios.csv").set_index("evento_id")
    kg_por_pez_muerto = eventos.loc[eventos["centro_id"] == caro, "alimento_por_pez_muerto_kg"].iloc[0]

    vale_alim_1 = META_PRIMER_CICLO * s["cosecha"]
    vale_alim_2 = s["cosecha"]
    vale_san = tuple(f * s["evento"] for f in EVITABLE_BROTE)

    def margen(vale, costo):            # (mínimo, máximo) en CLP millones
        lo = (vale[0] if isinstance(vale, tuple) else vale) - costo[1]
        hi = (vale[1] if isinstance(vale, tuple) else vale) - costo[0]
        return [round(lo, 1), round(hi, 1)]

    centro_ref = lambda r: round((r[0] + r[1]) / 2, 1)
    m_alim_1 = margen(vale_alim_1, COSTO_AUDITORIA_MM)
    m_san = margen(vale_san, COSTO_SANIDAD_MM)
    total = [round(m_alim_1[0] + m_san[0], 1), round(m_alim_1[1] + m_san[1], 1)]
    out = {
        "centro": cifras["centro_mas_caro"],
        "sobrecosto_mm_clp": s,
        "partes_suman_total": abs(s["cosecha"] + s["evento"] + s["basal"] - s["total"]) < 1e-6,
        "precio_medio_alimento_clp_kg": round(centro["costo_clp"] / centro["alimento_kg"], 1),
        "alimentacion": {"vale_primer_ciclo_mm": round(vale_alim_1, 1), "vale_segundo_ciclo_mm": round(vale_alim_2, 1),
                         "cuesta_mm": COSTO_AUDITORIA_MM, "cuesta_horas": HORAS_AUDITORIA,
                         "margen_primer_ciclo_mm": m_alim_1, "margen_primer_ciclo_ref_mm": centro_ref(m_alim_1)},
        "sanidad": {"vale_por_brote_mm": [round(v, 1) for v in vale_san], "cuesta_por_ciclo_mm": COSTO_SANIDAD_MM,
                    "margen_por_ciclo_con_brote_mm": m_san, "margen_ref_mm": centro_ref(m_san)},
        "margen_total_primer_ciclo_mm": total, "margen_total_ref_mm": centro_ref(total),
        "pez": {"kg_por_pez_cosechado": round(kg_por_pez_cosechado, 2), "kg_por_pez_muerto_brote": round(kg_por_pez_muerto, 2),
                "muerto_vs_cosechado_pct": round(100 * kg_por_pez_muerto / kg_por_pez_cosechado, 1)},
        "horas_planilla_ano": [12 * h for h in HORAS_PLANILLA_MES],
    }
    (RESULTS / "caso_negocio.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
