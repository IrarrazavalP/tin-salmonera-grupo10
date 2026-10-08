"""Un solo comando produce todas las cifras del informe:  python -m salmonera"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd

from . import graficos
from .config import ALTERNATIVAS, DATOS, PRINCIPAL, RESULTADOS
from .fuentes import cargar
from .metrica import calcular


def correr(datos: Path = DATOS, salida: Path = RESULTADOS) -> dict:
    inicio = time.time()
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "figuras").mkdir(exist_ok=True)

    print("1/4 Leyendo las cuatro fuentes…")
    f = cargar(datos)
    print(f"    dólar: {f.origen_dolar}")

    print("2/4 Calculando la métrica con la definición principal…")
    r = calcular(f, PRINCIPAL)

    print("3/4 Recalculando con cada definición alternativa…")
    sens = [{"definicion": "principal", **r.resumen}]
    for nombre, d in ALTERNATIVAS.items():
        sens.append({"definicion": nombre, **calcular(f, d).resumen})
    sens = pd.DataFrame(sens)

    print("4/4 Escribiendo resultados y gráficos…")
    cobertura = f.cobertura.tabla()
    pct_fuera = f.cobertura.porcentaje("operacion_diaria")
    r.por_centro.round(4).to_csv(salida / "indicadores_por_centro.csv")
    r.descomposicion.round(4).to_csv(salida / "descomposicion_centro_caro.csv", index=False)
    r.basal.to_csv(salida / "mortalidad_basal.csv", index=False)
    r.conciliacion.to_csv(salida / "conciliacion_eventos.csv", index=False)
    sens.to_csv(salida / "sensibilidad_definiciones.csv", index=False)
    cobertura.to_csv(salida / "cobertura.csv", index=False)
    r.hechos.drop(columns=["mes"]).to_csv(salida / "hechos_jaula_dia.csv", index=False)

    for fn in (graficos.costo_por_centro, graficos.fcr_por_centro, graficos.descomposicion,
               graficos.mortalidad_en_el_tiempo):
        fn(r, salida / "figuras")
    graficos.sensibilidad(sens, salida / "figuras")

    cifras = {
        **r.resumen,
        "cobertura_pct_jaula_dia_excluidos": round(pct_fuera, 2),
        "jaula_dias_analizados": int(len(r.hechos)),
        "dolar_origen": f.origen_dolar,
        "segundos": round(time.time() - inicio, 1),
    }
    (salida / "cifras.json").write_text(json.dumps(cifras, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nListo. Cifras principales:")
    for k, v in cifras.items():
        print(f"  {k}: {v}")
    print(f"\nResultados en {salida}")
    return cifras


def main() -> None:
    p = argparse.ArgumentParser(description="Cadena de datos del Grupo 10 (Salmonera, set 3).")
    p.add_argument("--datos", type=Path, default=DATOS, help="carpeta con el .sqlite, el .csv y el .json del caso")
    p.add_argument("--salida", type=Path, default=RESULTADOS)
    a = p.parse_args()
    correr(a.datos, a.salida)


if __name__ == "__main__":
    main()
