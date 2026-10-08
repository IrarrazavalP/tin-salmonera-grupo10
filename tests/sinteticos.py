"""Datos INVENTADOS con el mismo esquema que el caso, para probar la cadena.

No son los datos del caso ni se derivan de ellos: sólo imitan los nombres de
tablas y columnas, y el tipo de suciedad que el código tiene que aguantar.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import numpy as np

DIAS = 120
INICIO = date(2026, 1, 1)


def _num_chileno(x: float, decimales: int = 1) -> str:
    texto = f"{x:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def crear(carpeta: Path, semilla: int = 3) -> dict:
    rng = np.random.default_rng(semilla)
    carpeta.mkdir(parents=True, exist_ok=True)
    centros = [("C1", "Centro Norte", "Z1"), ("C2", "Centro Sur", "Z1"), ("C3", "Centro Isla", "Z2")]
    jaulas = [(f"J{c[-1]}{k}", c, 1000) for c, _, _ in centros for k in range(1, 4)]
    lotes = [(f"L{j[1:]}", c, j, "2025-12-01", "50.000") for j, c, _ in jaulas]

    filas = []
    for j, c, _ in jaulas:
        poblacion, peso = 50_000, 1.2 if c != "C3" else 3.0
        for d in range(DIAS):
            fecha = INICIO + timedelta(days=d)
            evento = c == "C2" and j == "J21" and 60 <= d <= 75
            muertos = int(rng.poisson(8 if not evento else 160))
            poblacion -= muertos
            fcr = 1.25 if c != "C1" else 1.45  # C1 come más por kilo ganado
            crecimiento = poblacion * peso * 0.008
            alimento = crecimiento * fcr
            peso += peso * 0.008
            biomasa = poblacion * peso
            # suciedad: fechas en tres formatos y números con formato chileno
            if d % 3 == 0:
                f_txt = fecha.strftime("%d-%m-%Y")
            elif d % 3 == 1:
                f_txt = fecha.isoformat()
            else:
                f_txt = fecha.strftime("%d/%m/%Y")
            filas.append((f_txt, c, j, f"L{j[1:]}", "E1", _num_chileno(alimento), muertos,
                          _num_chileno(poblacion, 0), _num_chileno(biomasa), _num_chileno(crecimiento),
                          "7,6", "Z1", fecha.month))
    # basura que tiene que quedar fuera de la cobertura
    filas.append(("sin dato", "C1", "J11", "L11", "E1", "10", 1, "100", "200", "1", "7", "Z1", 1))
    filas.append(((INICIO + timedelta(days=5)).isoformat(), "C1", "J11", "L11", "E1", "", 1, "100", "200", "1", "7", "Z1", 1))
    filas.append(((INICIO + timedelta(days=9)).isoformat(), None, "J12", "L12", "E1", "10", 1, "0", "200", "1", "7", "Z1", 1))

    with sqlite3.connect(carpeta / "origen_acuicultura.sqlite") as con:
        con.execute("CREATE TABLE zonas (zona_id TEXT, zona TEXT)")
        con.executemany("INSERT INTO zonas VALUES (?,?)", [("Z1", "Norte"), ("Z2", "Sur")])
        con.execute("CREATE TABLE centros (centro_id TEXT, nombre TEXT, zona_id TEXT)")
        con.executemany("INSERT INTO centros VALUES (?,?,?)", centros)
        con.execute("CREATE TABLE jaulas (jaula_id TEXT, centro_id TEXT, capacidad INTEGER)")
        con.executemany("INSERT INTO jaulas VALUES (?,?,?)", jaulas)
        con.execute("CREATE TABLE especies (especie_id TEXT, especie TEXT)")
        con.execute("INSERT INTO especies VALUES ('E1','Salmón del Atlántico')")
        con.execute("CREATE TABLE lotes (lote_id TEXT, centro_id TEXT, jaula_id TEXT, fecha_siembra TEXT, smolts_sembrados TEXT)")
        con.executemany("INSERT INTO lotes VALUES (?,?,?,?,?)", lotes)
        con.execute("""CREATE TABLE operacion_diaria (fecha TEXT, centro_id TEXT, jaula_id TEXT, lote_id TEXT,
            especie_id TEXT, alimento_kg TEXT, mortalidad_n INTEGER, poblacion TEXT, biomasa_kg TEXT,
            crecimiento_kg TEXT, temperatura_agua TEXT, zona TEXT, mes INTEGER)""")
        con.executemany("INSERT INTO operacion_diaria VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", filas)
        con.execute("CREATE TABLE cosechas (cosecha_id TEXT, lote_id TEXT, centro_id TEXT, fecha TEXT, kilos_vivos TEXT, kilos_producto TEXT, calibre TEXT)")
        ultimo = (INICIO + timedelta(days=DIAS - 1)).isoformat()
        con.execute("INSERT INTO cosechas VALUES ('K1','L31','C3',?,'150.000','120.000','4-5')", (ultimo,))

    precios = ["tipo_alimento;mes;precio_clp_kg;proveedor;moneda;glosa"]
    meses = ["ene-2026", "2026-02", "03-2026", "abril 2026"]
    for i, m in enumerate(meses):
        precios.append(f"Engorda 100;{m};1.450,5;Prov A;CLP;normal")
        precios.append(f"Engorda 200;{m};1.520;Prov B;CLP;")
        precios.append(f"Pigmentado;{m};1,95;Prov C;USD;importado")
    precios.append("Engorda 100;sin dato;1.400;Prov A;CLP;fila mala")
    (carpeta / "origen_costos_alimento.csv").write_bytes("\n".join(precios).encode("latin-1"))

    eventos = {"anio": 2026, "empresa": "Empresa inventada", "eventos": [
        {"evento_id": "EV1", "centro_id": "C2", "tipo": "SRS", "fecha_inicio": "2026-03-10",
         "fecha_fin": "2026-03-17", "mortalidad_asociada": 1800, "tratamiento": "antibiótico",
         "jaulas_afectadas": ["J21"]},
        {"evento_id": "EV2", "centro_id": "C3", "tipo": "Caligus", "fecha_inicio": "15-ene-2026",
         "fecha_fin": None, "mortalidad_asociada": 300, "tratamiento": "baño", "jaulas_afectadas": []},
    ]}
    (carpeta / "origen_eventos_sanitarios.json").write_text(json.dumps(eventos, ensure_ascii=False), encoding="utf-8")
    return {"filas_operacion": len(filas), "filas_basura": 3}


def dolar_falso(anio: int) -> list[dict]:
    return [{"fecha": f"{(date(anio, 1, 1) + timedelta(days=d)).isoformat()}T03:00:00.000Z", "valor": 950.0}
            for d in range(365)]
