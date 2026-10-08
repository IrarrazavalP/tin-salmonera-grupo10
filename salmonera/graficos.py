"""Las visualizaciones del informe: cada una con su unidad en el título y la fuente al pie."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from .config import FUENTE_PIE  # noqa: E402
from .metrica import Resultado  # noqa: E402

ACENTO, GRIS, ROJO = "#1f5f8b", "#9aa5ad", "#b03a2e"


def _cerrar(fig: plt.Figure, ruta: Path) -> None:
    fig.text(0.01, 0.01, FUENTE_PIE, fontsize=7, color="#555555", ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(ruta, dpi=200)
    plt.close(fig)


def costo_por_centro(r: Resultado, carpeta: Path) -> Path:
    c = r.por_centro.dropna(subset=["costo_clp_por_kg"]).sort_values("costo_clp_por_kg")
    fig, ax = plt.subplots(figsize=(7, 3.6))
    colores = [ROJO if i == r.centro_caro else GRIS for i in c.index]
    ax.barh(c.index.astype(str), c["costo_clp_por_kg"], color=colores)
    ax.set_title("Costo de alimento por kg ganado, por centro (CLP/kg)", loc="left", fontsize=11)
    ax.set_xlabel("CLP por kg de biomasa ganada")
    for y, v in enumerate(c["costo_clp_por_kg"]):
        ax.text(v, y, f" {v:,.0f}".replace(",", "."), va="center", fontsize=8)
    ruta = carpeta / "1_costo_por_centro.png"
    _cerrar(fig, ruta)
    return ruta


def fcr_por_centro(r: Resultado, carpeta: Path) -> Path:
    c = r.por_centro.dropna(subset=["fcr_economico"]).sort_values("fcr_economico")
    x = range(len(c))
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.bar([i - 0.2 for i in x], c["fcr_biologico"], width=0.4, color=ACENTO, label="FCR biológico (eficiencia)")
    ax.bar([i + 0.2 for i in x], c["fcr_economico"], width=0.4, color=GRIS, label="FCR económico (lo que se paga)")
    ax.set_xticks(list(x), c.index.astype(str))
    ax.set_title("FCR biológico y económico por centro (kg de alimento por kg)", loc="left", fontsize=11)
    ax.legend(fontsize=8, frameon=False)
    ruta = carpeta / "2_fcr_por_centro.png"
    _cerrar(fig, ruta)
    return ruta


def descomposicion(r: Resultado, carpeta: Path) -> Path:
    d = r.descomposicion
    fig, ax = plt.subplots(figsize=(7, 3.2))
    colores = [ROJO if v > 0 else ACENTO for v in d["aporte_clp_por_kg"]]
    ax.barh(d["factor"], d["aporte_clp_por_kg"], color=colores)
    ax.axvline(0, color="#333333", linewidth=0.8)
    ax.set_title(f"Por qué el centro {r.centro_caro} cuesta más que el resto (CLP/kg)", loc="left", fontsize=11)
    ax.set_xlabel("Aporte a la diferencia de costo por kg ganado (CLP/kg)")
    ax.invert_yaxis()
    ruta = carpeta / "3_descomposicion_centro_caro.png"
    _cerrar(fig, ruta)
    return ruta


def mortalidad_en_el_tiempo(r: Resultado, carpeta: Path) -> Path:
    h = r.hechos[r.hechos["centro_id"] == r.centro_caro]
    dia = h.groupby("fecha").agg(muertos=("mortalidad_n", "sum"), basal=("mortalidad_basal_n", "sum"),
                                 evento=("con_evento", "any"))
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.plot(dia.index, dia["muertos"], color=GRIS, linewidth=0.9, label="Mortalidad registrada")
    ax.plot(dia.index, dia["basal"], color=ACENTO, linewidth=1.2, label="Mortalidad basal esperada")
    ax.fill_between(dia.index, 0, dia["muertos"].max(), where=dia["evento"], color=ROJO, alpha=0.12,
                    label="Ventana de evento sanitario", step="mid")
    ax.set_title(f"Mortalidad diaria del centro {r.centro_caro} (peces por día)", loc="left", fontsize=11)
    ax.legend(fontsize=8, frameon=False)
    fig.autofmt_xdate()
    ruta = carpeta / "4_mortalidad_centro_caro.png"
    _cerrar(fig, ruta)
    return ruta


def sensibilidad(tabla: pd.DataFrame, carpeta: Path) -> Path:
    t = tabla.iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    colores = [ACENTO if n == "principal" else GRIS for n in t["definicion"]]
    ax.barh(t["definicion"], t["costo_clp_por_kg_centro"], color=colores)
    ax.set_title("Costo por kg del centro más caro bajo cada definición (CLP/kg)", loc="left", fontsize=11)
    for y, (v, c) in enumerate(zip(t["costo_clp_por_kg_centro"], t["centro_mas_caro"])):
        ax.text(v, y, f" {v:,.0f} · {c}".replace(",", "."), va="center", fontsize=8)
    ruta = carpeta / "5_sensibilidad_definiciones.png"
    _cerrar(fig, ruta)
    return ruta
