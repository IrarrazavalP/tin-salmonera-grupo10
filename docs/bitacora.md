# Bitácora de supuestos

Anexo obligatorio de la Entrega 1. Una fila por supuesto que mueve una cifra: qué se supuso, por qué, qué pasa si es falso, y quién lo decidió y cuándo.

Los supuestos marcados **«propuesta, por confirmar»** están implementados en el código pero falta que el grupo los apruebe. Al confirmarlos, cambia la columna *Quién y cuándo*.

## Decisiones de definición (sección 3 del plan, versión 3)

La métrica es **R = kg de alimento ÷ kg cosechados**, repartida en tres partes que suman el total: lo que comieron los peces cosechados (R_cosecha), los muertos en un evento sanitario (R_evento) y los muertos por mortalidad normal (R_basal). La propuso Luz María el 08-10 (plan de trabajo, versión 3). Cada decisión tiene su alternativa calculada en `results/sensibilidad_definiciones.csv`; la última columna dice cuánto mueve el resultado **con los datos del caso**.

| # | Decisión (principal) | Por qué | Alternativa y cuánto cambia | Quién y cuándo |
|---|---|---|---|---|
| 1 | Denominador: kg vivos cosechados del lote | Es lo que la empresa vende; los 42 lotes tienen cosecha en el período | Biomasa ganada (cosechado − biomasa del primer registro): R del centro más caro sube 11,7 % (1,74 → 1,94) y el reparto de la brecha casi no cambia (55/39/6) | Luz María, plan v3, 08-10 · **por acordar** |
| 2 | El costo se mide en kg de alimento. Al pasar a pesos: precio promedio mensual único, igual para todas las jaulas | Con precio único, toda diferencia entre centros la explican los kilos, no las compras (correo de la contraparte, punto 1) | Tipo de alimento según el peso del pez (< 1,5 kg engorda 100; 1,5 a 4 kg engorda 200; > 4 kg pigmentado; cortes propuestos por Pedro): los kilos no cambian, los pesos por kg bajan 2,5 % | Luz María, plan v3 · cortes **por confirmar** |
| 2b | Promedio simple, no ponderado por kilos comprados | **Medido:** la lista de precios no trae kilos comprados (columnas: tipo, mes, precio, proveedor, moneda, glosa) | No hay con qué ponderar | Medido con los datos, 08-10 |
| 2c | Toda la lista de precios viene en CLP, así que el dólar de mindicador.cl se usa para expresar los resultados en USD (promedio del período) | **Medido:** la columna `moneda` sólo dice CLP. El README del caso entrega el dólar como cuarta fuente | Si hubiera precios en USD, el código los convierte con el dólar promedio del mes | Medido con los datos, 08-10 |
| 3 | Alimento perdido en un pez muerto = lo que comió el pez promedio de su jaula hasta el día anterior (F3 y F4) | No depende del peso ni del FCR: es alimento efectivamente entregado. Los muertos no comen el día que mueren | Peso ganado por el pez promedio × FCR del lote hasta ese día: el alimento perdido por eventos sube 0,9 % | Luz María, plan v3 · forma exacta de la alternativa **por confirmar con Felipe (D)** |
| 4 | Mortalidad basal global: Σ muertos ÷ Σ población al inicio del día, en jaula-días fuera de toda ventana de evento. **Medido: 3,92 muertos por cada 10.000 peces al día** | Una sola tasa, fácil de explicar | Por etapa del ciclo (tramos de peso de la decisión 2): las tres tasas son casi iguales y el resultado cambia 0,1 punto. **La mortalidad normal no varía por etapa en estos datos** | Luz María, plan v3 · medido 10-10 |
| 5 | La ventana del evento va de la fecha de inicio a la fecha de fin que declara sanidad (**N = 0**) | **Medido (gráfico 3):** en el único evento con exceso visible, la mortalidad salta de 4 a unos 26 por 10.000 el mismo día declarado y vuelve a 4 al día siguiente del fin. No hay anticipo que capturar. Los 4 eventos traen fecha de fin | N = 7 días antes: el alimento perdido por eventos sube 0,3 % | Medido con los datos, 10-10 · **por acordar** (el plan dejaba N por definir) |
| 6 | Eventos sin jaulas identificadas se atribuyen al centro completo | Correo, punto 3 | Excluirlos: **no cambia nada**, porque los 4 eventos sin jaulas son de centros que no existen en la base (ver cobertura) | Plan de trabajo, 06-10 |
| 7 | Las muertes del evento son el exceso sobre la basal en la operación diaria | Tiene el grano jaula-día del modelo | La mortalidad que declara sanidad: el aporte del evento a la brecha sube de 39 % a 46 % y el de la basal baja a 0. `results/eventos_sanitarios.csv` muestra las dos cifras por evento | Plan de trabajo, 06-10 |
| 8 | La población registrada **todavía incluye** a los muertos del día: población al inicio = `poblacion`; comieron = `poblacion − mortalidad_n` | **Comprobación C1:** población(d) = población(d−1) − muertos(d−1) calza en el 100 % de los días; la lectura que proponía el plan (ya sin los muertos del día) calza en el 6 %. El plan decía usar la alternativa si la comprobación no calzaba | La lectura del plan: cambia 0,1 % el alimento perdido | Medido con los datos, 10-10 (`results/comprobaciones_registro.csv`) |
| 9 | **Nueva.** Un evento alcanza a todas las jaulas de su centro, no sólo a las que lista sanidad | **Medido:** en el evento SRS del centro 1 sanidad lista 4 jaulas, pero las otras 2 tienen exactamente el mismo salto de mortalidad en las mismas fechas (gráfico 3). La mortalidad que declara sanidad (62.478) calza con el centro completo (61.714) y no con las 4 jaulas (41.078) | Sólo las jaulas listadas: el aporte del evento a la brecha baja de 39 % a 26 % y el de la basal sube de 6 % a 20 %, porque esas muertes pasan a contarse como normales. **Es la decisión que más mueve la respuesta** | Propuesta Pedro (código), 10-10 · **por acordar con el grupo** |

## Supuestos de cálculo

| Supuesto | Por qué | Si fuera falso / alternativa | Quién y cuándo |
|---|---|---|---|
| El alimento acumulado por pez parte en el **primer registro** del lote (1 de enero de 2025), no en la siembra | **Medido:** el registro diario de las 42 jaulas empieza el 01-01-2025, aunque las siembras van de noviembre de 2024 a febrero de 2025. Lo que comieron antes no está en los datos | El alimento perdido queda subestimado en lo que comió el pez antes del primer registro (peces de 0,13 a 0,77 kg ese día) | Medido con los datos, 10-10 · el plan decía «desde la siembra» |
| Los peces muertos no comen el día que mueren | Plan v3, 4.4 | Si comieron, el alimento de los vivos queda sobreestimado y el perdido, subestimado | Luz María, plan v3 |
| Un pez muerto comió lo mismo que el pez promedio vivo de su jaula hasta el día anterior | Plan v3, 4.4 | El pez enfermo come menos: el alimento perdido queda levemente sobreestimado | Luz María, plan v3 |
| El ciclo de un lote termina el día de su cosecha; lo registrado después queda fuera | **Medido:** las 42 jaulas tienen una cosecha, su último registro previo es del mismo día y los kilos cosechados difieren de la biomasa registrada en 0,04 % en promedio. Después hay 69 registros sueltos (0,49 %) en que la población no refleja la cosecha | Cuenta en la cobertura. **Preguntar a la contraparte** qué son esos registros | Medido con los datos, 08-10 y 10-10 |
| `crecimiento_kg` es crecimiento de peces vivos (comprobación C2) | **Medido:** biomasa(d) = biomasa(d−1) + crecimiento(d) − muertos(d−1) × peso(d−1) calza en el 99,2 % de los días | Sólo se usa en la alternativa de la decisión 3 | Medido con los datos, 10-10 |
| El centro con más costo es el de mayor R | Es la métrica; con precio único, el orden en pesos por kg es el mismo | Ninguna alternativa cambia cuál es el centro más caro (el 1) | **Propuesta, por confirmar** |
| El exceso sobre la basal se calcula día a día y no puede ser negativo | Un día bajo la basal no «devuelve» muertes | En los eventos sin exceso real quedan entre 150 y 310 muertes atribuidas por ruido (menos de 0,8 % del total de eventos) | Propuesta Pedro (código), 10-10 |

## Límites de la separación

- **La eficiencia y el evento no son independientes.** R_cosecha del centro 1 es peor en sus tres especies (1,41 a 1,50, contra 1,05 a 1,26 en el resto). La métrica separa el alimento que se comieron los muertos del que se comieron los vivos, pero no puede decir cuánto de la peor eficiencia de los vivos se debe a que estuvieron enfermos durante el brote.
- **La mortalidad declarada no calza con la diaria en los eventos chicos.** En los otros tres eventos sanidad declara entre 2.790 y 8.420 muertes y la operación diaria no muestra ningún exceso sobre la basal en esas fechas (gráfico 3).

## Limpieza y cobertura

| Regla | Por qué | Efecto |
|---|---|---|
| Se excluye la fila jaula-día con fecha ilegible, sin jaula, o con alimento, mortalidad, población o biomasa ilegibles | Sin esos datos no se puede calcular ninguna de las tres partes de la métrica | Cuenta en la cobertura |
| Se excluyen población o biomasa ≤ 0, y alimento o mortalidad negativos | Valores imposibles | Cuenta en la cobertura |
| Si hay dos registros de la misma jaula el mismo día, se usa el primero | Duplicado | Cuenta en la cobertura (138 registros, 0,99 %) |
| Se excluyen los registros posteriores a la cosecha del lote | El ciclo terminó; ver *Supuestos de cálculo* | Cuenta en la cobertura (69 registros, 0,49 %) |
| El centro faltante se recupera desde el maestro de jaulas | La jaula determina el centro | No excluye la fila |
| Si un día declara 1.000 o más muertos y la población del día siguiente no cae en esa cantidad, se usa la caída real de población | **Medido:** 55 días tienen mortalidad de cinco cifras y en ninguno la población cae en esa cantidad; en 18 cae como si el número tuviera dos ceros de más. 3 de los 55 caen en la ventana de un evento | Se **corrige**, no se excluye: aparece en `cobertura.csv` como «corregido» |
| Se excluyen los eventos sanitarios de centros que no existen en la base de operaciones | **Medido:** 4 de los 8 eventos (justo los que vienen sin jaulas identificadas) son de centros con un id que no está en el maestro de centros | Por eso la decisión 6 (atribuir al centro o excluir) **no cambia el resultado** con estos datos: no hay a qué centro atribuirlos |
| Se excluyen las cosechas cuyo lote no está en el maestro de lotes | No se puede saber de qué jaula son | 6 de 48 cosechas |
| Un número con punto seguido de exactamente tres dígitos (`12.500`) se lee como miles; la temperatura, no | Formato chileno | **Revisar un par de casos a mano** |
| Un número con coma sola (`7,6`) se lee como decimal | Formato chileno | — |

La cifra de cobertura del informe es el **% de registros jaula-día excluidos: 1,48 %** (`cobertura_pct_jaula_dia_excluidos` en `cifras.json`): 0,99 % por duplicados y 0,49 % por ser posteriores a la cosecha. El detalle por fuente y por motivo está en `results/cobertura.csv`.
