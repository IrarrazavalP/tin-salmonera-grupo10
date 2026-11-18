## E. Caso de negocio y adopción

> Reemplaza el texto actual de la sección 4 «Evidencia y Recomendaciones» del informe, bajo su título. Las cifras salen de `results/cifras.json` y de `results/caso_negocio.json` (`python caso_negocio.py`, después de correr `entrega2.ipynb`). Los costos, la meta y la fracción evitable los dio la contraparte.

### Evidencia

El Centro 1 (Reloncaví) es el centro con más costo de la empresa. Usa **1,74 kg de alimento por kg cosechado**, contra 1,24 kg en los demás centros (imagen 1). La brecha de 0,51 kg/kg tiene las dos causas, aunque pesa más la eficiencia (imagen 2):

- **54 %:** menor eficiencia de los peces que sí se cosecharon.
- **39 %:** muertes del brote de SRS de agosto a octubre de 2025.
- **6 %:** mortalidad normal.

![Alimento consumido por kg cosechado](../figuras/1_R_por_centro.png)
**Imagen 1: Alimento usado por cada kg cosechado por centro**

![Brecha del centro caro](../figuras/2_brecha_centro_caro.png)
**Imagen 2: Brechas del centro 1 comparado con el resto de los centros**

En pesos, el Centro 1 gastó **CLP 729 millones** más en alimento que si hubiera rendido como el resto. De eso, **403 millones** vienen de la peor eficiencia de los peces cosechados, **282 millones** del alimento que comieron los peces que murieron en el brote y **44 millones** de la mortalidad normal.

El 18,0 % de todo el alimento del Centro 1 se lo comieron peces que nunca llegaron a cosecha: 11,4 % por el brote y 6,5 % por mortalidad normal (imagen 5, en el Anexo).

**Morir tarde cuesta más.** Un pez muerto en el brote ya había comido 4,9 kg de alimento. Eso es el 74 % de los 6,6 kg que come un pez del Centro 1 hasta su cosecha, así que el brote se llevó peces que ya habían comido tres cuartos de su alimento.

La peor eficiencia aparece en las tres especies del centro (imagen 4, en el Anexo), así que no se explica por la mezcla de especies.

### Cuánto vale y cuánto cuesta cada palanca

| Palanca | Vale: ahorro en alimento | Cuesta, según la contraparte | Margen |
|---|---|---|---|
| **Alimentación**: auditoría de la estrategia de alimentación del Centro 1. Decide el Gerente de Producción | CLP 202 millones en el primer ciclo, si se cierra la mitad de la brecha de eficiencia; CLP 403 millones desde el segundo ciclo | CLP 20 a 25 millones de asesoría externa, una vez, más unas 150 h de personal propio en 2 meses | **CLP 177 a 182 millones** en el primer ciclo |
| **Sanidad**: detección y tratamiento temprano de brotes. Decide el Gerente de Salud | CLP 85 a 113 millones por un brote como este (30 % a 40 % de 282 millones) | CLP 60 a 80 millones por ciclo | **CLP 5 a 53 millones** en un ciclo con brote; pierde 60 a 80 millones en un ciclo sin brote |
| Mortalidad normal | CLP 44 millones | — | Sin acción: es parecida en todos los centros |

**Cifra de referencia: un margen de unos CLP 208 millones en el primer ciclo, con un rango de 181 a 235 millones.** Es la suma de las dos palancas.

La alimentación va primero: aporta casi todo el margen y su costo se paga una sola vez. La detección temprana rinde poco por sí sola, y solo si hay un brote. Para que rinda, tiene que apuntar a dos cosas que muestran los datos:

- **Todo el centro, no solo las jaulas con síntomas.** La mortalidad subió el mismo día en las 6 jaulas del Centro 1, aunque sanidad registró solo 4 (sección C, decisión 9).
- **Los lotes cercanos a la cosecha,** donde un pez muerto ya comió la mayor parte de su alimento.

Los datos no muestran cuántos días antes se podría detectar un brote. La mortalidad salta de 3,9 a 32 muertos por cada 10.000 peces el mismo día en que sanidad lo declara, el 01-08-2025, y no antes (imagen 3, en el Anexo).

**Supuestos.**

- **Margen directo.** El caso no trae precios de venta, así que el valor es ahorro de costo de alimento, que es margen directo.
- **Precio del alimento.** Se usa el de 2025, en promedio CLP 1.123 por kg en el Centro 1.
- **Meta de alimentación.** La contraparte espera un R de 1,45 a 1,50 en el primer ciclo, lo que equivale a cerrar la mitad de la brecha, y el nivel del resto en el segundo. Aquí esa meta se aplica solo a la parte de eficiencia, que es lo conservador: la parte del brote depende de que haya brotes.
- **De dónde salen los costos.** Los costos, la meta y el 30 % a 40 % evitable los dio la contraparte; no salen de los datos del caso.

### Prueba ácida

- **Qué decisión:** intervenir el Centro 1 en alimentación, en sanidad o en ambas, según qué parte del sobrecosto domine.
- **Quién decide:** el Gerente de Producción si es eficiencia y el Gerente de Salud si es brote. El Gerente General aprueba el presupuesto adicional, que ambas acciones necesitan.
- **Con qué frecuencia:** una vez al mes, en el comité de producción, con datos a más tardar 15 días después del cierre de mes.

### Qué reemplaza

El tablero reemplaza la **planilla Excel del FCR bruto** que arma el analista de control de gestión con datos que exporta del sistema de producción. Hoy le toma de 12 a 15 horas al mes, entre consolidar los centros y corregir diferencias, es decir, de **144 a 180 horas al año** que quedan libres.

Lo que se reemplaza es la planilla, no el indicador: el FCR bruto (1,74 en el Centro 1) se sigue reportando al directorio. Por eso el tablero lo muestra junto al desglose, que es la condición que puso la contraparte.

### Plan de adopción

| Casilla | Plan |
|---|---|
| Primer usuario | El Gerente de Producción, en el comité de producción de diciembre de 2026, con los datos de noviembre |
| Qué puede hacer que no lo use, y qué lo protege | **1.** El directorio sigue pidiendo el FCR bruto y la planilla sigue viva → el tablero muestra el FCR bruto con la misma definición, para reportarlo desde ahí. **2.** Desconfianza porque sanidad informa otras cifras de muertes → la pantalla muestra las dos fuentes y por qué difieren. **3.** Datos atrasados o una corrida fallida → el acuerdo de servicio fija 15 días de plazo, las pruebas que bloquean impiden publicar cifras malas y el pie muestra la fecha de la última versión publicada. **4.** Nadie corre la cadena → se corre con un solo comando y un README, y la opera el mismo analista que hoy arma la planilla |
| Métrica de adopción y fecha | El comité usa el tablero en las 3 sesiones de diciembre de 2026 a febrero de 2027, y desde la sesión de febrero de 2027 la planilla ya no se prepara (0 horas al mes) |
| Quién lo sostiene | Es dueño el Gerente de Producción y lo opera el analista de control de gestión. Es una propuesta del grupo, igual que el acuerdo de servicio de la sección B |

### Evaluación de la contraparte

Le preguntamos a la contraparte si la pantalla le serviría, qué reemplazaría y qué meta le parece realista. Respondió así (verbalizado, correo de Sergio Bocaz del jueves 12-11-2026, 10:36, respuesta a nuestras consultas del 11-11-2026; el hilo completo va en el Anexo E):

- **Si le sirve:** «Sí, nos serviría, porque hoy vemos el sobrecosto como un solo número y no sabemos si el problema es de alimentación o sanitario.»
- **Qué reemplaza:** «La pantalla no reemplazaría el indicador, porque el FCR bruto lo seguimos reportando al directorio y lo usamos para compararnos con la industria. Sí reemplazaría la planilla y el trabajo manual, siempre que muestre el FCR bruto junto con el desglose.»
- **La meta:** «Una meta razonable para el primer ciclo es 1,45 a 1,50, es decir, cerrar cerca de la mitad de la brecha, y alcanzar el nivel del resto de los centros en el segundo ciclo. Sobre el brote, estimamos que con una detección más temprana se puede evitar entre un 30% y un 40% del efecto.»

Las tres condiciones se cumplen:

- El tablero separa el sobrecosto en sus causas.
- Muestra el FCR bruto junto al desglose.
- Las cifras de margen usan la meta y la fracción evitable que dio la contraparte.

### Anexo E

- Imagen 3: Mortalidad diaria en torno a cada evento sanitario
- Imagen 4: Eficiencia por centro y especie
- Imagen 5: Porcentaje de alimento que consumieron los peces que murieron por centro
- Hilo de correo con la contraparte: consultas del Grupo 10 (11-11-2026, 23:37) y respuesta de Sergio Bocaz (12-11-2026, 10:36)

### Trazabilidad de las cifras

| Cifra en el texto | Valor exacto | De dónde sale |
|---|---|---|
| 1,74 y 1,24 kg/kg; brecha 0,51 | 1,744854 · 1,238295 · 0,506559 | `cifras.json` → `R` |
| 54 %, 39 %, 6 % | 54,44 · 39,39 · 6,17 | `cifras.json` → `aporte_brecha_pct` |
| CLP 403, 282, 44 y 729 millones | 403,16 · 282,35 · 43,82 · 729,32 | `cifras.json` → `sobrecosto_mm_clp` |
| 18,0 % / 11,4 % / 6,5 % del alimento | 17,97 · 11,45 · 6,52 | `indicadores_por_centro.csv` → `pct_evento`, `pct_basal` |
| 4,9 kg por pez muerto; 6,6 kg por pez cosechado; 74 % | 4,88 · 6,59 · 74,0 | `caso_negocio.json` → `pez` |
| Salto de 3,9 a 32 por 10.000 el 01-08-2025 | 3,86 → 32,16 | `mortalidad_en_torno_a_eventos.csv` (EV-8001, días −1 y 0) |
| CLP 202 y 403 millones (alimentación) | 201,6 · 403,2 | `caso_negocio.json` → `alimentacion` |
| CLP 85 a 113 millones (sanidad) | 84,7 · 112,9 | `caso_negocio.json` → `sanidad` |
| Margen 177–182 y 5–53 millones | | `caso_negocio.json` → `margen_primer_ciclo_mm`, `margen_por_ciclo_con_brote_mm` |
| Referencia 208 millones (181–235) | 207,9 · 181,3 · 234,5 | `caso_negocio.json` → `margen_total_*` |
| CLP 1.123 por kg de alimento | 1.122,9 | `caso_negocio.json` → `precio_medio_alimento_clp_kg` |
| 144 a 180 horas al año | | `caso_negocio.json` → `horas_planilla_ano` |
| Costos, meta, fracción evitable y horas de la planilla | | Contraparte, correo del 12-11-2026 (constantes al inicio de `caso_negocio.py`) |
