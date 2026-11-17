# Salmonera · Grupo 10 (S3) · IIC3752 Entrega 2

Cadena de datos y prototipo que responden la pregunta de la gerencia:

> En el centro con más costo, ¿la causa es la mortalidad de un evento sanitario, un FCR peor, o ambas? ¿Se pueden separar?

Se integran las cuatro fuentes del caso (SQLite, CSV, JSON y la API de mindicador.cl) en una tabla de **una fila por jaula y día** y se calcula cuántos kg de alimento usa cada centro por kg cosechado (**R**), repartido en tres partes que suman el total: peces cosechados (eficiencia), muertos en un evento sanitario y muertos por mortalidad normal.

## Qué hay en el repositorio

| Ruta | Qué es |
|---|---|
| `entrega2.ipynb` | **Cadena de la Entrega 2**, por capas (cruda → depurada → modelo → consumo), con pruebas de calidad en cada corrida |
| `calidad.py` | Pruebas de calidad que usa `entrega2.ipynb` (qué verifica, qué hace si falla: avisa o bloquea) |
| `entrega1.ipynb` | Cadena de la Entrega 1, tal como se entregó (no se modifica) |
| `prototipo/` | Prototipo en Tableau (`PrototipoFinal.twbx`) y sus tablas `datos/`, que escribe `entrega2.ipynb`; ver `prototipo/README.md` |
| `figuras/` | Las 5 visualizaciones del informe |
| `docs/` | Ficha de la métrica, hallazgos, bitácora de supuestos, evidencia y recomendaciones, declaración de uso de IA |
| `requirements.txt` | Versiones con las que se reproducen las cifras (Python 3.11) |

## Cómo reproducirlo

Requisitos: Python 3.11 o superior e internet (consulta a mindicador.cl; si falla se usa la copia de `data/cache/`).

```bash
git clone <url de este repositorio>
cd tin-salmonera-grupo10
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Los datos del caso **no están en el repositorio** (son de la empresa). Déjalos en `data/` con estos nombres:

```
data/origen_acuicultura.sqlite
data/origen_costos_alimento.csv
data/origen_eventos_sanitarios.json
```

Un solo comando, desde la raíz del repositorio:

```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 entrega2.ipynb
```

**Cuánto demora:** unos minutos como máximo (timeout 900 s), más la consulta a la API.

**Qué se espera:** se escriben `results/`, `figuras/` y las tablas del prototipo en `prototipo/datos/` **solo si pasan las pruebas que bloquean**; `results/calidad.csv` y `results/estado_corrida.json` dicen qué pasó. Si una prueba solo avisa, la corrida sigue y queda registrada. Si la API del dólar falla, se usa la última copia guardada o se declara "sin dato".

## La métrica

```
R = alimento total (kg) ÷ kg cosechados = R_cosecha + R_evento + R_basal

R_cosecha = alimento de los peces que llegaron a la cosecha          → eficiencia (FCR)
R_evento  = alimento de los peces muertos en un evento (exceso sobre la basal)
R_basal   = alimento de los peces muertos por mortalidad normal
```

Las diferencias entre el centro más caro y el resto se reparten entre las tres partes sin residuo. Las decisiones de definición y sus alternativas están en `docs/ficha_metrica.md`; cada supuesto, en `docs/bitacora.md`.

## Prototipo

`prototipo/PrototipoFinal.twbx` (Tableau Desktop 2025.2 o superior, solo local: no publicar en Tableau Public / Cloud). `PrototipoFinal.twbx` es el libro empaquetado (con su copia de las tablas): se abre sin más, en cualquier computador. `PrototipoFinal-vivo.twb` lee en vivo `prototipo/datos/`, que escribe `entrega2.ipynb` en la misma corrida. Detalle y cómo actualizar: `prototipo/README.md`.

> Nota: algunos documentos de `docs/` (`hallazgos.md`, `revision_notebook_martin.md`) son de la Entrega 1 y mencionan el comando `python -m salmonera`, que ya no existe; la cadena vigente es `entrega2.ipynb`.
