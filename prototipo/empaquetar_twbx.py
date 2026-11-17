"""Arma PrototipoFinal.twbx (en la raíz del repositorio) a partir de PrototipoFinal-vivo.twb y las tablas de datos/.

Uso (desde la raíz del repositorio o desde prototipo/):
    python3 prototipo/empaquetar_twbx.py

El .twbx lleva su propia copia de las tablas (Data/datos/) y apunta a ella con rutas relativas,
así que abre en cualquier computador con Tableau Desktop. Hay que volver a correrlo cada vez que
se corre entrega2.ipynb si se quiere que el .twbx tenga la última corrida.
"""
import re
import sys
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VIVO, DATOS = AQUI / "PrototipoFinal-vivo.twb", AQUI / "datos"
SALIDA = AQUI.parent / "PrototipoFinal.twbx"     # en la raíz del repositorio, como dicen los README

texto = VIVO.read_text(encoding="utf-8")
rutas = set(re.findall(r"directory='([^']*/datos)'", texto))
if not rutas:
    sys.exit("No encontré las conexiones a datos/ en PrototipoFinal-vivo.twb")
for ruta in rutas:                      # rutas absolutas del computador donde se guardó -> relativa dentro del paquete
    texto = texto.replace(f"directory='{ruta}'", "directory='Data/datos'")
usados = sorted(set(re.findall(r"filename='([^'/]+\.csv)'", texto)))
faltan = [f for f in usados if not (DATOS / f).exists()]
if faltan:
    sys.exit(f"Faltan en prototipo/datos/: {faltan}. Corre entrega2.ipynb primero.")

with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("PrototipoFinal.twb", texto)
    for f in usados:
        z.write(DATOS / f, f"Data/datos/{f}")
print(f"Listo: {SALIDA.name} con {len(usados)} tablas")
