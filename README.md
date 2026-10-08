# Salmonera · Grupo 10 (S3) · IIC3752 Entrega 1

Cadena de datos que responde la pregunta de la gerencia:

> En el centro con más costo, ¿la causa es la mortalidad de un evento sanitario, un FCR peor, o ambas? ¿Se pueden separar?

Lee las cuatro fuentes del caso (SQLite, CSV, JSON y la API de mindicador.cl), las integra en una tabla con **una fila por jaula y día**, y calcula el costo de alimento por kg ganado de cada centro, separado en tres factores: **precio del alimento**, **eficiencia (FCR biológico)** y **mortalidad** (basal y por evento sanitario). Todas las cifras del informe salen de este código.

## Cómo reproducirlo

Requisitos: Python 3.11 o superior y conexión a internet (para mindicador.cl). No hace falta Java ni Spark.

```bash
git clone <url de este repositorio>
cd tin-salmonera-grupo10
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copia los tres archivos del caso (set `grupo_s3`) en `data/raw/`:

```
data/raw/origen_acuicultura.sqlite
data/raw/origen_costos_alimento.csv
data/raw/origen_eventos_sanitarios.json
```

Los datos del caso **no están en el repositorio**: son de la empresa, y la regla del curso prohíbe subirlos a servicios externos.

Luego, un solo comando:

```bash
python -m salmonera
```

**Cuánto demora:** unos segundos, más la consulta a mindicador.cl.

**Qué se ve al final:** las cifras principales impresas en la terminal, y en `results/`:

| Archivo | Qué es |
|---|---|
| `cifras.json` | Las cifras que cita el informe: centro más caro, costo por kg, FCR, aporte de cada factor, costo de la mortalidad por evento y cobertura |
| `indicadores_por_centro.csv` | Alimento, biomasa ganada y muerta, los dos FCR, el FCR bruto que usa la gerencia, precio medio y costo por kg de cada centro |
| `descomposicion_centro_caro.csv` | Cuánto de la diferencia de costo (centro caro vs. el resto) aporta cada factor, en CLP/kg y en % |
| `sensibilidad_definiciones.csv` | El resultado bajo la definición principal y bajo cada alternativa (decisiones 2 a 7 del plan) |
| `conciliacion_eventos.csv` | Mortalidad declarada por sanidad vs. la que suma la operación diaria en la ventana de cada evento |
| `mortalidad_basal.csv` | Tasa diaria normal usada como línea base |
| `cobertura.csv` | Registros excluidos de cada fuente y por qué |
| `hechos_jaula_dia.csv` | La tabla de hechos completa (una fila es una jaula en un día) |
| `figuras/` | Las 5 visualizaciones del informe, con unidad en el título y fuente al pie |

Si mindicador.cl no responde, se usa la última copia guardada en `data/cache/`, y `cifras.json` lo declara en `dolar_origen`.

## La métrica

```
FCR biológico = alimento (kg) ÷ (biomasa ganada + biomasa muerta)     → eficiencia del alimento
FCR económico = alimento (kg) ÷ biomasa ganada                         → lo que paga la empresa
Costo por kg  = precio × FCR biológico × (1 + biomasa muerta ÷ biomasa ganada)
```

- **Biomasa ganada** (por jaula y lote): biomasa final − biomasa inicial + kilos vivos cosechados.
- **Biomasa muerta**: peces muertos × peso promedio de la jaula (biomasa ÷ población).
- **Exceso por evento**: mortalidad sobre la basal en los días de la ventana de un evento sanitario.
- **Descomposición**: como el costo es un producto de factores, su logaritmo es una suma, y la diferencia entre el centro caro y el resto se reparte entre precio, FCR, mortalidad basal y mortalidad por evento, sin residuo.
- Se muestra también el FCR bruto de la gerencia (alimento ÷ biomasa final), sólo como referencia.

Las decisiones de definición, con su alternativa, están en `salmonera/config.py`. Cada supuesto está en [`docs/bitacora.md`](docs/bitacora.md).

## Estructura

```
salmonera/
  config.py     rutas y decisiones de definición (principal y alternativas)
  limpieza.py   lectura de números, fechas y meses sucios; registro de cobertura
  fuentes.py    lectura de las cuatro fuentes
  metrica.py    tabla jaula-día, basal, exceso por evento, FCR y descomposición
  graficos.py   las 5 visualizaciones
  __main__.py   el comando único
tests/          pruebas con datos INVENTADOS (no son del caso)
notebooks/      exploración inicial de Martín (sin salidas)
docs/           bitácora de supuestos y declaración de uso de IA
```

## Pruebas

```bash
python -m pytest
```

Corren con un set de datos inventado (`tests/sinteticos.py`) que imita el esquema y los formatos sucios del caso, y con la API simulada. Comprueban que la cadena corre de punta a punta, que la identidad de la ficha cuadra, que la descomposición no deja residuo y que la cobertura cuenta exactamente las filas inválidas.
