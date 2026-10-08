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
| 2d | Los precios en dólares (`moneda` = USD) se pasan a CLP con el dólar observado promedio del mes (mindicador.cl) | Es para lo que entra la API al análisis; el promedio mensual calza con el grano mensual de la lista de precios | Usar el dólar del primer día del mes movería poco | **Propuesta, por confirmar con el README** |
| 3 | El pez muerto se valoriza al peso promedio de su jaula ese día (biomasa ÷ población del registro) | Criterio validado por la contraparte (correo, punto 2). Sobreestima levemente, porque el pez enfermo pesa menos | Alternativa: peso del día anterior. Falta declarar si población y biomasa están antes o después de descontar los muertos: **revisar en el README** | Contraparte, correo de octubre |
| 4 | Mortalidad basal por etapa del ciclo (mismos tramos de peso de 2), con jaula-días sin evento | La mortalidad normal de un smolt no es la de un pez de cosecha | Alternativa: una basal global | Plan de trabajo, 06-10 |
| 5 | La ventana de un evento empieza **7 días antes** de la fecha declarada y termina en la fecha de fin | La detección es reactiva y la fecha de inicio llega tarde (acta y correo, punto 3). 7 días es un valor inicial: el plan pide fijar N mirando cuándo la mortalidad se separa de la basal | Alternativa: desde la fecha declarada (N = 0). **N = 7 por confirmar con el gráfico 4** | **Propuesta, por confirmar** |
| 5b | Un evento sin fecha de fin dura hasta el último día con registros | No hay otra fecha de cierre | Alargar el evento sube el exceso atribuido | **Propuesta, por confirmar** |
| 6 | Eventos sin jaulas identificadas se atribuyen a todas las jaulas de su centro | Correo, punto 3: hay que decidir y dejarlo escrito | Alternativa: excluirlos | Plan de trabajo, 06-10 |
| 7 | La mortalidad del evento es el exceso sobre la basal en la operación diaria | Tiene el grano jaula-día del modelo; la de sanidad es por evento y la llena otra área | Alternativa: la mortalidad declarada por sanidad, valorizada al peso medio de la ventana. La tabla `conciliacion_eventos.csv` muestra cuánto difieren | Plan de trabajo, 06-10 |

## Supuestos de cálculo

| Supuesto | Por qué | Si fuera falso | Quién y cuándo |
|---|---|---|---|
| Biomasa ganada = final − inicial + kilos vivos cosechados, por jaula y lote | Es la ganancia neta de biomasa del período | Si la biomasa del registro ya descuenta la cosecha del día, se cuenta dos veces: **revisar en el README** | **Propuesta, por confirmar** |
| Si el lote se cosechó en o después de su último registro, la biomasa que queda es la última menos lo cosechado (nunca negativa) | El último registro todavía incluye a los peces que se cosecharon | Sin esta regla, los peces cosechados se cuentan en la biomasa final y en la cosecha | **Propuesta, por confirmar** |
| La biomasa inicial es la del primer registro del lote | Los registros empiezan después de la siembra | Se pierde el crecimiento entre la siembra y el primer registro (pequeño) | **Propuesta, por confirmar** |
| El resultado se compara contra `crecimiento_kg` sumado (columna `crecimiento_registrado_kg`) | Sirve de control cruzado de la biomasa ganada | Si difieren mucho, alguna de las dos lecturas está mal: **revisar con los datos** | **Propuesta, por confirmar** |
| El centro más caro es el de mayor costo de alimento por kg ganado (FCR económico × precio) | Es el costo que paga la empresa por kilo producido | Con el FCR bruto de la gerencia el orden podría cambiar | **Propuesta, por confirmar** |

## Limpieza y cobertura

| Regla | Por qué | Efecto |
|---|---|---|
| Se excluye la fila jaula-día con fecha ilegible, sin jaula, o con alimento, mortalidad, población o biomasa ilegibles | Sin esos datos no se puede calcular ninguna de las tres partes de la métrica | Cuenta en la cobertura |
| Se excluyen población o biomasa ≤ 0, y alimento o mortalidad negativos | Valores imposibles | Cuenta en la cobertura |
| Si hay dos registros de la misma jaula el mismo día, se usa el primero | Duplicado | Cuenta en la cobertura |
| El centro faltante se recupera desde el maestro de jaulas | La jaula determina el centro | No excluye la fila |
| Un número con punto seguido de exactamente tres dígitos (`12.500`) se lee como miles; la temperatura, no | Formato chileno | **Revisar un par de casos a mano** |
| Un número con coma sola (`7,6`) se lee como decimal | Formato chileno | — |

La cifra de cobertura del informe es el **% de registros jaula-día excluidos** (`cobertura_pct_jaula_dia_excluidos` en `cifras.json`). El detalle por fuente y por motivo está en `results/cobertura.csv`.
