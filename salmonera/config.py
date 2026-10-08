"""Rutas y decisiones de definición del análisis.

Cada decisión de la sección 2 del plan de trabajo tiene una opción PRINCIPAL y
una ALTERNATIVA. El informe usa la principal; la alternativa se calcula igual
para mostrar cuánto cambia el resultado (lo pide la contraparte en el correo).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data" / "raw"
CACHE = RAIZ / "data" / "cache"
RESULTADOS = RAIZ / "results"

FUENTE_PIE = (
    "Fuente: origen_acuicultura.sqlite, origen_costos_alimento.csv, "
    "origen_eventos_sanitarios.json y mindicador.cl. Cálculo: Grupo 10."
)


@dataclass(frozen=True)
class Decisiones:
    # 2. Precio del alimento: "mensual" (promedio único del mes) o "por_etapa"
    #    (tipo de alimento según el peso promedio del pez de la jaula).
    precio: str = "mensual"
    # Cortes de peso (kg) para "por_etapa": < corte_100 → engorda 100,
    # < corte_200 → engorda 200, resto → pigmentado. Supuesto del grupo.
    corte_100: float = 1.5
    corte_200: float = 4.0
    # 3. Peso con que se valoriza un pez muerto: "mismo_dia" (biomasa ÷ población
    #    del registro de ese día) o "dia_anterior" (el de la jaula el día previo).
    peso_muerto: str = "mismo_dia"
    # 4. Mortalidad basal: "por_etapa" (por tramo de peso) o "global".
    basal: str = "por_etapa"
    # 5. Días que la ventana de un evento se extiende antes de la fecha declarada.
    ventana_previa_dias: int = 7
    # 6. Eventos sin jaulas identificadas: "centro" (todas las jaulas del centro)
    #    o "excluir".
    sin_jaulas: str = "centro"
    # 7. Mortalidad del evento: "diaria" (exceso sobre la basal en la operación
    #    diaria) o "sanidad" (la mortalidad declarada por evento).
    mortalidad: str = "diaria"


PRINCIPAL = Decisiones()

# Una alternativa por decisión: se cambia una a la vez, el resto queda en la principal.
ALTERNATIVAS: dict[str, Decisiones] = {
    "2 · precio por etapa": replace(PRINCIPAL, precio="por_etapa"),
    "3 · peso del día anterior": replace(PRINCIPAL, peso_muerto="dia_anterior"),
    "4 · basal global": replace(PRINCIPAL, basal="global"),
    "5 · ventana desde la fecha declarada": replace(PRINCIPAL, ventana_previa_dias=0),
    "6 · excluir eventos sin jaulas": replace(PRINCIPAL, sin_jaulas="excluir"),
    "7 · mortalidad declarada por sanidad": replace(PRINCIPAL, mortalidad="sanidad"),
}
