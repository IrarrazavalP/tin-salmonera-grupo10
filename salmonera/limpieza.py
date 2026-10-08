"""Conversión de textos sucios a números y fechas, y registro de cobertura.

Las fuentes "no son archivos limpios" (correo de la contraparte): números con
separador de miles chileno, comas decimales, fechas en varios formatos y meses
escritos con letras. Todo lo que no se puede leer se excluye y se cuenta.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime

import pandas as pd

BASURA = {"", "sin dato", "s/d", "sd", "n/a", "na", "nan", "null", "none", "total", "-", "--", "?"}

MESES = {
    "enero": 1, "ene": 1, "febrero": 2, "feb": 2, "marzo": 3, "mar": 3,
    "abril": 4, "abr": 4, "mayo": 5, "may": 5, "junio": 6, "jun": 6,
    "julio": 7, "jul": 7, "agosto": 8, "ago": 8, "septiembre": 9, "setiembre": 9,
    "sep": 9, "sept": 9, "set": 9, "octubre": 10, "oct": 10, "noviembre": 11,
    "nov": 11, "diciembre": 12, "dic": 12,
    # por si algún registro viene en inglés
    "january": 1, "jan": 1, "february": 2, "april": 4, "apr": 4, "august": 8,
    "aug": 8, "december": 12, "dec": 12,
}


def _sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def es_basura(valor: object) -> bool:
    if valor is None:
        return True
    if isinstance(valor, float) and math.isnan(valor):
        return True
    return str(valor).strip().lower() in BASURA


def a_numero(valor: object, miles_posible: bool = True) -> float | None:
    """'1.234,5' → 1234.5 · '7,6' → 7.6 · '12.500' → 12500 · '3.25' → 3.25.

    Un punto seguido de exactamente tres dígitos (y nada más) se lee como
    separador de miles, salvo que la columna no admita miles (temperatura).
    """
    if es_basura(valor):
        return None
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor)
    s = str(valor).strip().lower().replace(" ", "").replace(" ", "")
    s = re.sub(r"(clp|usd|us\$|\$|kg|kilos?|°c|ºc|c$|unid\.?|u$)", "", s)
    if s in BASURA:
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    elif "." in s and miles_posible and re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def a_entero(valor: object) -> float | None:
    """Conteos (peces, smolts): todo lo que no sea dígito se ignora."""
    if es_basura(valor):
        return None
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor)
    digitos = re.sub(r"[^0-9-]", "", str(valor).split(",")[0])
    return float(digitos) if digitos not in ("", "-") else None


def _mes_en_texto(s: str) -> str:
    for nombre in sorted(MESES, key=len, reverse=True):
        s = re.sub(rf"(?<![a-z]){nombre}(?![a-z])", f"{MESES[nombre]:02d}", s)
    return s


FORMATOS_FECHA = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%y", "%d/%m/%y", "%d.%m.%Y", "%Y%m%d")


def a_fecha(valor: object) -> date | None:
    if es_basura(valor):
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    s = _sin_tildes(str(valor).strip().lower())
    s = re.split(r"[t\s]", s, maxsplit=1)[0] if re.match(r"\d{4}-\d{2}-\d{2}[t\s]", s) else s
    s = _mes_en_texto(s).replace(" de ", "-").replace(" ", "-")
    for formato in FORMATOS_FECHA:
        try:
            f = datetime.strptime(s, formato).date()
        except ValueError:
            continue
        if f.year < 100:  # '26-10-08' leído al revés
            continue
        return f
    return None


def a_mes(valor: object) -> pd.Period | None:
    """Mes de la lista de precios: '2026-03', '03-2026', 'mar-26', 'marzo 2026', '2026-03-01'."""
    if es_basura(valor):
        return None
    f = a_fecha(valor)
    if f is not None:
        return pd.Period(year=f.year, month=f.month, freq="M")
    s = _mes_en_texto(_sin_tildes(str(valor).strip().lower()))
    numeros = re.findall(r"\d+", s)
    if len(numeros) < 2:
        return None
    a, b = numeros[0], numeros[1]
    if len(a) == 4:
        anio, mes = int(a), int(b)
    elif len(b) == 4:
        anio, mes = int(b), int(a)
    else:
        anio, mes = 2000 + int(b), int(a)
    return pd.Period(year=anio, month=mes, freq="M") if 1 <= mes <= 12 else None


def a_id(valor: object) -> str | None:
    """Identificadores comparables entre fuentes: sin espacios, en mayúscula, '7.0' → '7'."""
    if es_basura(valor):
        return None
    s = str(valor).strip().upper()
    return s[:-2] if re.fullmatch(r"\d+\.0", s) else s


@dataclass
class Cobertura:
    """Cuántos registros entran y cuántos quedan fuera de cada fuente, y por qué."""

    filas: list[dict] = field(default_factory=list)
    correcciones: list[dict] = field(default_factory=list)

    def corregir(self, fuente: str, motivo: str, n: int) -> None:
        """Registros que se corrigen (no se excluyen): se informan aparte."""
        if n:
            self.correcciones.append({"fuente": fuente, "motivo": motivo, "registros": n})

    def registrar(self, fuente: str, total: int, motivos: dict[str, int]) -> None:
        excluidos = sum(motivos.values())
        self.filas.append({"fuente": fuente, "total": total, "excluidos": excluidos, "motivos": motivos})

    def tabla(self) -> pd.DataFrame:
        filas = []
        for f in self.filas:
            if not f["motivos"]:
                filas.append({"fuente": f["fuente"], "motivo": "—", "registros": 0, "total": f["total"]})
            for motivo, n in f["motivos"].items():
                filas.append({"fuente": f["fuente"], "motivo": motivo, "registros": n, "total": f["total"]})
        for c in self.correcciones:
            total = next((f["total"] for f in self.filas if f["fuente"] == c["fuente"]), 0)
            filas.append({"fuente": c["fuente"], "motivo": f"corregido (no excluido): {c['motivo']}",
                          "registros": c["registros"], "total": total})
        tabla = pd.DataFrame(filas)
        if not tabla.empty:
            tabla["porcentaje"] = (100 * tabla["registros"] / tabla["total"].where(tabla["total"] > 0)).round(2)
        return tabla

    def porcentaje(self, fuente: str) -> float:
        for f in self.filas:
            if f["fuente"] == fuente and f["total"]:
                return 100 * f["excluidos"] / f["total"]
        return 0.0
