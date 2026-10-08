from __future__ import annotations

import json
import math
from datetime import date

import pytest

from salmonera import fuentes
from salmonera.config import PRINCIPAL
from salmonera.limpieza import a_fecha, a_mes, a_numero

from .sinteticos import crear, dolar_falso


class _Respuesta:
    def __init__(self, anio: int) -> None:
        self._anio = anio

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"serie": dolar_falso(self._anio)}


@pytest.fixture
def datos(tmp_path, monkeypatch):
    info = crear(tmp_path / "raw")
    monkeypatch.setattr(fuentes, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(fuentes.requests, "get", lambda url, timeout: _Respuesta(int(url.rstrip("/").split("/")[-1])))
    return tmp_path, info


@pytest.mark.parametrize("texto, esperado", [
    ("1.234,5", 1234.5), ("7,6", 7.6), ("12.500", 12500.0), ("3.25", 3.25), ("1,234.5", 1234.5),
    ("$ 1.450", 1450.0), ("sin dato", None), ("", None), (None, None), (42, 42.0),
])
def test_numeros(texto, esperado):
    assert a_numero(texto) == esperado


def test_temperatura_no_se_lee_como_miles():
    assert a_numero("7.600", miles_posible=False) == 7.6


@pytest.mark.parametrize("texto", ["2026-03-10", "10-03-2026", "10/03/2026", "10-mar-2026", "2026-03-10T00:00:00"])
def test_fechas(texto):
    assert a_fecha(texto) == date(2026, 3, 10)


@pytest.mark.parametrize("texto", ["2026-03", "03-2026", "mar-2026", "marzo 2026", "2026-03-01"])
def test_meses(texto):
    assert str(a_mes(texto)) == "2026-03"


def test_cadena_completa_corre_y_cuadra(datos):
    from salmonera.__main__ import correr
    from salmonera.metrica import calcular

    carpeta, info = datos
    cifras = correr(carpeta / "raw", carpeta / "results")

    # todas las salidas existen
    for nombre in ("cifras.json", "indicadores_por_centro.csv", "cobertura.csv", "sensibilidad_definiciones.csv",
                   "conciliacion_eventos.csv", "hechos_jaula_dia.csv"):
        assert (carpeta / "results" / nombre).exists(), nombre
    assert len(list((carpeta / "results" / "figuras").glob("*.png"))) == 5

    # la cobertura cuenta exactamente las filas basura inventadas
    esperado = 100 * info["filas_basura"] / info["filas_operacion"]
    assert cifras["cobertura_pct_jaula_dia_excluidos"] == pytest.approx(esperado, abs=0.01)

    f = fuentes.cargar(carpeta / "raw")
    r = calcular(f, PRINCIPAL)
    c = r.por_centro
    # identidad de la ficha: costo/kg = precio × FCR biológico × (1 + muerta/ganada)
    identidad = c["precio_medio_clp_kg"] * c["fcr_biologico"] * c["factor_mortalidad"]
    assert (identidad - c["costo_clp_por_kg"]).abs().max() < 1e-6
    # la descomposición reparte toda la diferencia, sin residuo
    diferencia = cifras["costo_clp_por_kg_centro"] - cifras["costo_clp_por_kg_resto"]
    assert r.descomposicion["aporte_clp_por_kg"].sum() == pytest.approx(diferencia, abs=0.2)
    assert sum(cifras[k] for k in cifras if k.startswith("aporte_pct")) == pytest.approx(100, abs=0.5)
    # en los datos inventados C1 tiene peor FCR y C2 el evento: el más caro es C1 y lo explica el FCR
    assert cifras["centro_mas_caro"] == "C1"
    assert cifras["aporte_pct_fcr"] > 50
    assert c.loc["C2", "exceso_evento_kg"] > 0
    assert c.loc["C1", "exceso_evento_kg"] == 0
    # FCR económico ≥ biológico siempre (la mortalidad sólo puede encarecer)
    assert (c["fcr_economico"] >= c["fcr_biologico"]).all()


def test_las_alternativas_mueven_lo_que_deben(datos):
    from salmonera.config import ALTERNATIVAS
    from salmonera.metrica import calcular

    carpeta, _ = datos
    f = fuentes.cargar(carpeta / "raw")
    base = calcular(f, PRINCIPAL)
    sin_jaulas = calcular(f, ALTERNATIVAS["6 · excluir eventos sin jaulas"])
    # el evento de C3 no trae jaulas: al excluirlo, C3 queda sin exceso por evento
    assert base.por_centro.loc["C3", "exceso_evento_kg"] >= sin_jaulas.por_centro.loc["C3", "exceso_evento_kg"]
    assert sin_jaulas.por_centro.loc["C3", "exceso_evento_kg"] == 0
    etapa = calcular(f, ALTERNATIVAS["2 · precio por etapa"])
    # con precio por etapa, C3 (peces grandes) paga pigmentado: su precio medio cambia
    assert not math.isclose(etapa.por_centro.loc["C3", "precio_medio_clp_kg"],
                            base.por_centro.loc["C3", "precio_medio_clp_kg"])


def test_sin_api_usa_la_copia_local(datos, monkeypatch):
    carpeta, _ = datos
    fuentes.cargar(carpeta / "raw")  # deja la copia en cache

    def caida(url, timeout):
        raise fuentes.requests.ConnectionError("sin red")

    monkeypatch.setattr(fuentes.requests, "get", caida)
    f = fuentes.cargar(carpeta / "raw")
    assert "copia local" in f.origen_dolar
