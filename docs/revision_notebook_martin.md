# Qué se tomó del notebook de Martín y qué cambió

`notebooks/entrega1_martin.ipynb` es la exploración inicial (07-10), guardada sin salidas. La cadena de `salmonera/` parte de su lectura de las cuatro fuentes y de su lógica de basal y exceso, y corrige lo siguiente. Se revisó **sólo el código**: los datos del caso no se miraron.

| Lo que hacía el notebook | Problema | Cómo quedó |
|---|---|---|
| Spark (PySpark 3.5.3) | Requiere Java instalado: es lo que más arriesga que corra «de cero en un ambiente limpio» | pandas, sin Java |
| `arreglar_kg` convierte a `integer` | Corta los decimales de los kilos (el comentario decía `Double`) | Se leen como decimales |
| Quita todos los puntos y cambia comas por puntos | Un `3.25` escrito con punto decimal se volvía `325` | Se distinguen miles (`12.500`) de decimales (`3.25`) |
| Las limpiezas de kg, temperatura y smolts quedan en `diccionario_dfs` | El análisis sigue usando las tablas anteriores a esas limpiezas, y la de temperatura guarda una tupla | Cada tabla se limpia una vez y es la que se usa |
| La sección «precio» repite la de smolts | El precio nunca se limpia; el análisis usa la tabla `productos` original | Se lee el precio y se pasa a CLP según `moneda` |
| El precio mensual se cruza sólo por número de mes | Enero de dos años distintos se mezclaría | Se cruza por año y mes |
| Dólar sólo de 2026 | Si los datos abarcan otro año, no hay tipo de cambio | Se pide cada año presente en los datos |
| `date_sub` no está importado | El paso de la ventana de eventos falla | Corregido |
| Los eventos se cruzan por `jaula_id` sin desarmar `jaulas_afectadas` | La columna no existe en esa tabla: el cruce falla | Se desarma la lista; los eventos sin jaulas se tratan según la decisión 6 |
| No calcula el FCR | Falta la métrica de la pregunta | FCR biológico, económico y bruto, y la descomposición del costo |
| La cobertura se imprime por tabla | El informe pide un número | `cobertura_pct_jaula_dia_excluidos` y `results/cobertura.csv` |
| `%pip install` dentro del notebook | No es reproducible fuera de Colab/VS Code | `requirements.txt` y un solo comando |
