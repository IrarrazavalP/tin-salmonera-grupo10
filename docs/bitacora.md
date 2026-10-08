# Bitácora de supuestos

Anexo obligatorio de la Entrega 1. Una fila por supuesto que mueve una cifra: qué se supuso, por qué, qué pasa si es falso, y quién lo decidió y cuándo.

Los supuestos marcados **«propuesta, por confirmar»** están implementados en el código pero falta que el grupo los apruebe. Al confirmarlos, cambia la columna *Quién y cuándo*.

## Decisiones de definición (sección 2 del plan)

| # | Supuesto (principal) | Por qué | Si fuera falso / alternativa | Quién y cuándo |
|---|---|---|---|---|
| 1 | La biomasa muerta cuenta como ganada en el FCR biológico; el FCR económico usa sólo la biomasa viva o cosechada | El pez que murió comió: el biológico mide eficiencia, el económico lo que paga la empresa, y su distancia es lo que cuesta la mortalidad | Se informan los dos, siempre | Plan de trabajo, 06-10 |
| 2 | Precio: promedio mensual único, igual para todas las jaulas | Deja el precio constante entre centros, así que toda la diferencia de costo la explican los kilos, es decir el FCR (correo de la contraparte, punto 1) | Alternativa: tipo de alimento según el peso del pez (< 1,5 kg engorda 100; 1,5 a 4 kg engorda 200; > 4 kg pigmentado). Cortes: **propuesta, por confirmar** | Propuesta Pedro (código), 08-10 |
| 2b | Precio simple, no ponderado por kilos comprados | La lista de precios no trae kilos comprados por tipo, así que no hay con qué ponderar | Si existiera esa columna, el promedio ponderado bajaría el peso del pigmentado si se compra poco | **Propuesta, por confirmar** |
| 2c | Un mes sin lista de precios usa el precio del último mes anterior que sí tiene | No hay otra fuente de precio | Cambia el costo de ese mes; se ve en la sensibilidad si hay muchos meses faltantes | **Propuesta, por confirmar** |
| 2d | Toda la lista de precios viene en CLP (medido: la columna `moneda` sólo dice CLP), así que el dólar de mindicador.cl se usa para expresar los resultados en USD, con el promedio del período | Es lo que la empresa entrega como cuarta fuente (README: dólar observado 2025) | Si hubiera precios en USD, el código los convierte con el dólar promedio del mes | Medido con los datos, 08-10 |
| 2e | Los meses de operación sin lista de precios (6 de 18, la cola de 2026 con pocas filas) usan el precio del último mes de 2025 | La lista de Abastecimiento cubre sólo 2025 | Afecta muy pocos jaula-días; ver cobertura | **Propuesta, por confirmar** |
| 3 | El pez muerto se valoriza al peso promedio de su jaula ese día (biomasa ÷ población del registro) | Criterio validado por la contraparte (correo, punto 2). Sobreestima levemente, porque el pez enfermo pesa menos. **Medido:** la población y la biomasa del registro están **antes** de descontar los muertos del día (en el 98 % de los días, la población de hoy es la de ayer menos los muertos de ayer) | Alternativa: peso del día anterior | Contraparte, correo de octubre · lectura del registro medida el 08-10 |
| 4 | Mortalidad basal por etapa del ciclo (mismos tramos de peso de 2), con jaula-días sin evento | La mortalidad normal de un smolt no es la de un pez de cosecha | Alternativa: una basal global | Plan de trabajo, 06-10 |
| 5 | La ventana de un evento empieza **7 días antes** de la fecha declarada y termina en la fecha de fin | La detección es reactiva y la fecha de inicio llega tarde (acta y correo, punto 3). 7 días es un valor inicial: el plan pide fijar N mirando cuándo la mortalidad se separa de la basal | Alternativa: desde la fecha declarada (N = 0). **N = 7 por confirmar con el gráfico 4** | **Propuesta, por confirmar** |
| 5b | Un evento sin fecha de fin dura hasta el último día con registros | No hay otra fecha de cierre | Alargar el evento sube el exceso atribuido | **Propuesta, por confirmar** |
| 6 | Eventos sin jaulas identificadas se atribuyen a todas las jaulas de su centro | Correo, punto 3: hay que decidir y dejarlo escrito | Alternativa: excluirlos | Plan de trabajo, 06-10 |
| 7 | La mortalidad del evento es el exceso sobre la basal en la operación diaria | Tiene el grano jaula-día del modelo; la de sanidad es por evento y la llena otra área | Alternativa: la mortalidad declarada por sanidad, valorizada al peso medio de la ventana. La tabla `conciliacion_eventos.csv` muestra cuánto difieren | Plan de trabajo, 06-10 |

## Supuestos de cálculo

| Supuesto | Por qué | Si fuera falso / alternativa | Quién y cuándo |
|---|---|---|---|
| **8.** El crecimiento bruto es Σ `crecimiento_kg`; la biomasa ganada neta es ese crecimiento menos la biomasa muerta | **Medido:** en el 99 % de los días, biomasa de hoy − biomasa de ayer + peso de los muertos = `crecimiento_kg`. Es bruto: incluye a los peces que después mueren. Con esta lectura los 7 centros tienen FCR plausibles | Alternativa: ganada neta = biomasa final − inicial. Con ella 2 centros quedan con FCR biológico fuera de rango, porque hay saltos de 30 a 59 días sin registro en algunas jaulas | Medido con los datos, 08-10 |
| **9.** Se incluyen los días registrados después de la cosecha de cada jaula | **Medido:** los kilos cosechados igualan la biomasa registrada ese día, pero en 36 de 42 jaulas el registro diario sigue después de la cosecha sin descontarla (la población no baja). El registro diario es la fuente de la métrica | Alternativa: cortar cada jaula en su fecha de cosecha. **Preguntar a la contraparte** qué son esos días | Medido con los datos, 08-10 · **decisión por confirmar** |
| Las cosechas no se suman a la biomasa ganada | Como el registro no descuenta la cosecha, sumarla cuenta dos veces los mismos peces | `results/conciliacion_cosechas.csv` muestra cada cosecha frente al registro | Medido con los datos, 08-10 |
| El centro más caro es el de mayor costo de alimento por kg ganado neto (precio × FCR económico) | Es el costo que paga la empresa por kilo producido | Sólo la alternativa 8 cambia cuál es el centro más caro (ver `sensibilidad_definiciones.csv`) | **Propuesta, por confirmar** |

## Limpieza y cobertura

| Regla | Por qué | Efecto |
|---|---|---|
| Se excluye la fila jaula-día con fecha ilegible, sin jaula, o con alimento, mortalidad, población o biomasa ilegibles | Sin esos datos no se puede calcular ninguna de las tres partes de la métrica | Cuenta en la cobertura |
| Se excluyen población o biomasa ≤ 0, y alimento o mortalidad negativos | Valores imposibles | Cuenta en la cobertura |
| Si hay dos registros de la misma jaula el mismo día, se usa el primero | Duplicado | Cuenta en la cobertura |
| El centro faltante se recupera desde el maestro de jaulas | La jaula determina el centro | No excluye la fila |
| Si un día declara 1.000 o más muertos y la población del día siguiente no cae en esa cantidad, se usa la caída real de población | **Medido:** 55 días tienen mortalidad de cinco cifras y en ninguno la población cae en esa cantidad; en 18 cae como si el número tuviera dos ceros de más. Sólo 1 de los 55 está en la ventana de un evento | Se **corrige**, no se excluye: aparece en `cobertura.csv` como «corregido» |
| Se excluyen los eventos sanitarios de centros que no existen en la base de operaciones | **Medido:** 4 de los 8 eventos (justo los que vienen sin jaulas identificadas) son de centros con un id que no está en el maestro de centros | Por eso la decisión 6 (atribuir al centro o excluir) **no cambia el resultado** con estos datos: no hay a qué centro atribuirlos |
| Se excluyen las cosechas cuyo lote no está en el maestro de lotes | No se puede saber de qué jaula son | 6 de 48 cosechas |
| Un número con punto seguido de exactamente tres dígitos (`12.500`) se lee como miles; la temperatura, no | Formato chileno | **Revisar un par de casos a mano** |
| Un número con coma sola (`7,6`) se lee como decimal | Formato chileno | — |

La cifra de cobertura del informe es el **% de registros jaula-día excluidos** (`cobertura_pct_jaula_dia_excluidos` en `cifras.json`). El detalle por fuente y por motivo está en `results/cobertura.csv`.
