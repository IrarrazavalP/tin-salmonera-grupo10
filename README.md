# Salmonera · Grupo 10 (S3) · IIC3752 Entrega 1

Cadena de datos que responde la pregunta de la gerencia:

> En el centro con más costo, ¿la causa es la mortalidad de un evento sanitario, un FCR peor, o ambas? ¿Se pueden separar?

Lee las cuatro fuentes del caso (SQLite, CSV, JSON y la API de mindicador.cl), las integra en una tabla con **una fila por jaula y día**, y calcula cuántos kg de alimento usa cada centro por kg cosechado (**R**), repartidos en tres partes que suman el total: lo que comieron los **peces cosechados** (eficiencia), los **muertos en un evento sanitario** y los **muertos por mortalidad normal**. Todas las cifras del informe salen de este código.

## Cómo reproducirlo

Requisitos: Python 3.11 o superior y conexión a internet (para bajar los datos del caso y consultar mindicador.cl). No hace falta Java ni Spark.

```bash
git clone <url de este repositorio>
cd tin-salmonera-grupo10
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Los datos del caso **no están en este repositorio**: el comando los baja solo, la primera vez, desde el repositorio público del curso (`LMD18/IIC3752-2026-2-Proyecto-Semestral`, carpeta `casos/salmonera/grupo_3`, fijo en el commit `67055a6`) a `data/raw/`. Si prefieres copiarlos a mano, déjalos ahí con estos nombres:

```
data/raw/origen_acuicultura.sqlite
data/raw/origen_costos_alimento.csv
data/raw/origen_eventos_sanitarios.json
```

Luego, un solo comando:

```bash
python -m salmonera
```

**Cuánto demora:** unos segundos, más la consulta a mindicador.cl.

**Qué se ve al final:** las cifras principales impresas en la terminal, y en `results/`:

| Archivo | Qué es |
|---|---|
| `cifras.json` | Las cifras que cita el informe: centro más caro, R y sus tres partes, cuánto de la brecha explica cada una, el sobrecosto en pesos, el evento más caro y la cobertura |
| `indicadores_por_centro.csv` | Alimento, kg cosechados, R, sus tres partes (en kg/kg, en % del alimento y en CLP/kg) y el R bruto de la gerencia, por centro |
| `indicadores_por_especie.csv`, `indicadores_por_centro_especie.csv`, `indicadores_por_lote.csv` | Lo mismo, abierto por especie, por centro × especie y por lote |
| `brecha_centro_caro.csv` | La diferencia de R entre el centro más caro y el resto, repartida entre las tres partes, en kg/kg, en % y en pesos |
| `sensibilidad_definiciones.csv` | El resultado bajo la definición principal y bajo cada alternativa (decisiones 1 a 9), con cuánto cambia |
| `eventos_sanitarios.csv` | Cada evento: mortalidad declarada por sanidad vs. la de la operación diaria (jaulas listadas y centro completo), alimento perdido en kg y pesos, alimento por pez muerto y días que faltaban para la cosecha |
| `mortalidad_en_torno_a_eventos.csv` | Mortalidad diaria antes, durante y después de cada evento, en las jaulas listadas y en las demás del centro (fija la ventana) |
| `comprobaciones_registro.csv` | Comprobaciones C1 y C2 del plan: cómo hay que leer la población y el crecimiento del registro diario |
| `conciliacion_cosechas.csv` | Cada cosecha frente a la biomasa registrada ese día |
| `mortalidad_basal.csv` | Tasa diaria normal usada como línea base |
| `cobertura.csv` | Registros excluidos de cada fuente y por qué |
| `hechos_jaula_dia.csv` | La tabla de hechos completa (una fila es una jaula en un día) |
| `figuras/` | Las 5 visualizaciones del informe, con unidad en el título y fuente al pie |

Si mindicador.cl no responde, se usa la última copia guardada en `data/cache/`, y `cifras.json` lo declara en `dolar_origen`.

## La métrica

```
R = alimento total (kg) ÷ kg cosechados = R_cosecha + R_evento + R_basal

R_cosecha = alimento que comieron los peces que llegaron a la cosecha     → eficiencia (FCR)
R_evento  = alimento que comieron los peces muertos en un evento sanitario (exceso sobre la basal)
R_basal   = alimento que comieron los peces muertos por mortalidad normal
```

- **Alimento perdido en un pez muerto**: lo que comió el pez promedio de su jaula desde el primer registro hasta el día anterior a su muerte. Por eso una muerte cerca de la cosecha cuesta más que una al inicio del ciclo.
- **Mortalidad basal**: muertos ÷ población al inicio del día, en los jaula-días fuera de la ventana de todo evento.
- **Muertes de evento**: dentro de la ventana, lo que excede a la basal; el resto es basal.
- **Agregación**: por centro, especie o centro × especie se suman numeradores y denominadores de los lotes y recién entonces se divide.
- **Brecha**: la diferencia de R entre el centro más caro y el resto es la suma de las diferencias de las tres partes, sin residuo.
- **Pesos**: la misma cuenta se repite valorizando el alimento de cada día al precio promedio del mes. El precio no entra a la métrica, sólo a la conversión final.
- Se muestra también el R bruto de la gerencia (alimento ÷ biomasa final), sólo como referencia.

Las fórmulas son las F1 a F15 del plan de trabajo (versión 3) y están en `salmonera/metrica.py`. Las decisiones de definición, con su alternativa, están en `salmonera/config.py`. Cada supuesto está en [`docs/bitacora.md`](docs/bitacora.md).

## Estructura

```
salmonera/
  config.py     rutas y decisiones de definición (principal y alternativas)
  limpieza.py   lectura de números, fechas y meses sucios; registro de cobertura
  fuentes.py    lectura de las cuatro fuentes
  metrica.py    tabla jaula-día, basal, muertes de evento, R en tres partes y brecha
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

Corren con un set de datos inventado (`tests/sinteticos.py`) que imita el esquema y los formatos sucios del caso, y con la API simulada. Comprueban que la cadena corre de punta a punta, que las tres partes suman R y el 100 % del alimento, que la brecha se reparte sin residuo, que el alimento de la cosecha es el de los peces sobrevivientes y que la cobertura cuenta exactamente las filas excluidas.
