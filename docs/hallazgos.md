# Hallazgos de los datos

Lo que fuimos descubriendo al mirar las cuatro fuentes del caso (Salmonera, set 3). Sirve para tres cosas: la tabla de hallazgos del mandato (A), la ficha de la métrica (D) y la recomendación (E).

Cada hallazgo dice si es **medido** (sale de un cálculo que cualquiera puede repetir) o **inferido** (es nuestra lectura de lo medido). Los supuestos y decisiones que se tomaron a partir de ellos están en [`bitacora.md`](bitacora.md); aquí va sólo lo que dicen los datos.

Las cifras salen de `python -m salmonera` con la métrica del plan de trabajo, versión 3 (R = kg de alimento ÷ kg cosechados). Entre paréntesis, el archivo de `results/` donde se ve cada una.

> **Estado al 10-10-2026.** El código que produce estas cifras está en el computador de Pedro y todavía no se sube a `main`. Los hallazgos marcados **por acordar** dependen de una decisión que el grupo no ha cerrado.

## 1. La respuesta a la pregunta

| # | Hallazgo | Tipo | Dónde se ve |
|---|---|---|---|
| 1.1 | El centro con más costo es el **1 (Reloncaví)**: usa 1,74 kg de alimento por kg cosechado, contra 1,23 del resto de los centros juntos. Ninguna definición alternativa cambia cuál es el centro más caro | Medido | `indicadores_por_centro.csv`, `sensibilidad_definiciones.csv` |
| 1.2 | La brecha con el resto (0,51 kg por kg) se reparte así: **55 % peor eficiencia** de los peces cosechados, **39 % muertes del evento sanitario**, **6 % mortalidad normal**. Son ambas causas, y se pueden separar | Medido · **por acordar** (depende del hallazgo 3.3) | `brecha_centro_caro.csv`, gráfico 2 |
| 1.3 | En pesos, el centro 1 gastó unos CLP 731 millones más en alimento de lo que habría gastado rindiendo como el resto: 406 por eficiencia, 281 por el evento y 44 por mortalidad normal | Medido · **por acordar** | `cifras.json` (`sobrecosto_clp_*`) |
| 1.4 | La peor eficiencia del centro 1 aparece en sus **tres especies** (1,41 a 1,50 kg por kg, contra 1,05 a 1,26 en los demás centros). No es un problema de una especie | Medido | `indicadores_por_centro_especie.csv`, gráfico 4 |
| 1.5 | La eficiencia y el evento no son independientes: los peces que sobrevivieron al brote probablemente comieron y crecieron peor mientras estuvieron enfermos. La métrica separa el alimento de los muertos del de los vivos, pero no puede decir cuánto de la peor eficiencia de los vivos se debe al brote | Inferido | — |
| 1.6 | El R bruto que usa hoy la gerencia (alimento ÷ biomasa final) da casi lo mismo que nuestro R total (1,74 en el centro 1): el aporte de la métrica no es un número distinto, es poder repartirlo | Medido | `indicadores_por_centro.csv` (`R_bruto_gerencia`) |

## 2. Morir tarde cuesta más

| # | Hallazgo | Tipo | Dónde se ve |
|---|---|---|---|
| 2.1 | Un pez muerto en el SRS del centro 1 (unos 83 días antes de la cosecha) ya se había comido **4,9 kg** de alimento. Uno muerto en el SRS del centro 2 (unos 205 días antes), **2,3 kg**. La misma muerte cuesta el doble si ocurre cerca de la cosecha | Medido | `eventos_sanitarios.csv` (`alimento_por_pez_muerto_kg`, `dias_a_cosecha_promedio`) |
| 2.2 | El evento más caro, por lejos, es el SRS del centro 1: CLP 281 millones de alimento perdido. Los otros tres suman cerca de CLP 2 millones | Medido · **por acordar** | `eventos_sanitarios.csv` |

## 3. Los eventos sanitarios

| # | Hallazgo | Tipo | Dónde se ve |
|---|---|---|---|
| 3.1 | El archivo de sanidad trae 8 eventos. **4 son de centros que no existen** en la base de operaciones, y son justo los 4 que vienen sin jaulas identificadas. Quedan 4 eventos utilizables | Medido | `cobertura.csv` |
| 3.2 | **Sólo uno de los 4 eventos se nota en la mortalidad diaria**: el SRS del centro 1 (1 de agosto al 15 de octubre de 2025), donde la mortalidad pasa de unos 4 a unos 26 peces por cada 10.000 al día. En los otros tres (Caligus centro 5, Branquitis centro 7, SRS centro 2) la mortalidad no se mueve de la basal | Medido | `mortalidad_en_torno_a_eventos.csv`, gráfico 3 |
| 3.3 | En el SRS del centro 1 sanidad lista 4 jaulas afectadas (1 a 4), pero **las jaulas 5 y 6 tienen el mismo salto de mortalidad en las mismas fechas** | Medido | gráfico 3 (panel del centro 1) |
| 3.4 | La mortalidad que declara sanidad para ese evento (**62.478**) calza con las 6 jaulas del centro (**61.714**) y no con las 4 listadas (**41.078**) | Medido | `eventos_sanitarios.csv` |
| 3.5 | La lista de jaulas afectadas de ese evento está incompleta en el registro de sanidad: el brote afectó al centro completo | Inferido de 3.3 y 3.4 · **por acordar** cómo se trata | — |
| 3.6 | Si se usan sólo las 4 jaulas listadas, las muertes del brote en las jaulas 5 y 6 se cuentan como mortalidad normal: el evento baja de 39 % a 26 % de la brecha y la mortalidad normal sube de 6 % a 20 %. **Es la definición que más mueve la respuesta** | Medido | `sensibilidad_definiciones.csv` (fila 9) |
| 3.7 | La mortalidad sube **el mismo día** que sanidad declara como inicio y vuelve a la basal al día siguiente de la fecha de fin. En estos datos no hay días previos que capturar: adelantar la ventana 7 días cambia el resultado en 0,3 % | Medido | gráfico 3, `sensibilidad_definiciones.csv` (fila 5) |
| 3.8 | Lo anterior no calza con lo que dijo el cliente (la detección es reactiva y la fecha de inicio es imprecisa). Puede ser que el registro se haya corregido después, o que estos datos no reflejen ese problema | Inferido | — |
| 3.9 | En los tres eventos sin exceso visible, sanidad declara entre 2.790 y 8.420 muertes, mientras la operación diaria registra entre 500 y 1.500 en esas jaulas y fechas, todas dentro de lo normal. **Las dos fuentes no concilian** en esos eventos | Medido | `eventos_sanitarios.csv` |

## 4. La mortalidad normal

| # | Hallazgo | Tipo | Dónde se ve |
|---|---|---|---|
| 4.1 | La mortalidad basal es de **3,92 peces por cada 10.000 al día**, calculada fuera de las fechas de todo evento | Medido | `mortalidad_basal.csv` |
| 4.2 | **No varía con la etapa del ciclo**: 3,94, 3,91 y 3,93 por 10.000 en los tres tramos de peso. Usar una basal global o una por etapa cambia el resultado en 0,1 punto | Medido | `sensibilidad_definiciones.csv` (fila 4) |
| 4.3 | Fuera del brote, el centro 1 tiene la misma mortalidad normal que los demás (3,8 a 4,0 por 10.000 en sus seis jaulas) | Medido | `hechos_jaula_dia.csv` |

## 5. Cómo hay que leer el registro diario

| # | Hallazgo | Tipo | Dónde se ve |
|---|---|---|---|
| 5.1 | La población registrada cada día **todavía incluye a los peces que mueren ese día**: población de hoy = población de ayer − muertos de ayer, en el 100 % de los días. La lectura contraria (que ya venga descontada) calza en el 6 % | Medido (comprobación C1 del plan) | `comprobaciones_registro.csv` |
| 5.2 | `crecimiento_kg` es crecimiento de peces vivos y la biomasa descuenta aparte a los muertos: calza en el 99,2 % de los días | Medido (comprobación C2 del plan) | `comprobaciones_registro.csv` |
| 5.3 | El registro de las 42 jaulas **empieza el 1 de enero de 2025**, aunque las fechas de siembra van de noviembre de 2024 a febrero de 2025. Lo que comieron los peces antes de esa fecha no está en los datos, y ese día ya pesaban entre 0,13 y 0,77 kg | Medido | `indicadores_por_lote.csv` (`primer_registro`) |
| 5.4 | **14 de los 42 lotes tienen fecha de siembra posterior al primer registro** de su jaula (siembras hasta febrero de 2025, registros desde el 1 de enero). Una de las dos fechas no puede estar bien | Medido | tabla `lotes` de la base |
| 5.5 | Los smolts sembrados son iguales a la población del primer registro en los 42 lotes: el registro parte con el lote completo, sin mortalidad previa | Medido | tabla `lotes` de la base |
| 5.6 | Hay 55 días con mortalidad de cinco cifras que la población del día siguiente no refleja; en 18 la caída real es como si el número tuviera dos ceros de más. Son errores de digitación: se corrigen con la caída real de población, no se excluyen | Medido | `cobertura.csv` |
| 5.7 | Faltan 68 días sueltos en medio de los ciclos (saltos de 2 días en el registro de una jaula) | Medido | `hechos_jaula_dia.csv` |

## 6. Lotes y cosechas

| # | Hallazgo | Tipo | Dónde se ve |
|---|---|---|---|
| 6.1 | Hay 42 jaulas y 42 lotes, **un lote por jaula**, y cada uno tiene exactamente una cosecha en el período (20 de octubre, 20 de noviembre o 20 de diciembre de 2025). No hay lotes sin cosechar | Medido | `conciliacion_cosechas.csv` |
| 6.2 | Los kilos cosechados coinciden con la biomasa registrada ese mismo día (diferencia media de 0,04 %) | Medido | `conciliacion_cosechas.csv` |
| 6.3 | La tabla de cosechas trae 48 filas; 6 son de lotes que no existen en el maestro de lotes | Medido | `cobertura.csv` |
| 6.4 | Después de la cosecha quedan **69 registros sueltos** (hasta junio de 2026) en que la jaula sigue con población y alimento como si no se hubiera cosechado. Quedan fuera del análisis. Vale la pena preguntarle a la contraparte qué son | Medido | `cobertura.csv` |
| 6.5 | Hay tres especies (Salmón del Atlántico, 26 lotes; Coho, 10; Trucha, 6), repartidas de forma desigual: el centro 4 sólo tiene Atlántico y los centros 3 y 5 no tienen Trucha | Medido | `indicadores_por_centro_especie.csv` |
| 6.6 | Por especie, el alimento por kg cosechado es parecido: Coho 1,33, Atlántico 1,29, Trucha 1,25. La diferencia entre centros es mucho mayor que entre especies | Medido | `indicadores_por_especie.csv` |

## 7. Precios y dólar

| # | Hallazgo | Tipo | Dónde se ve |
|---|---|---|---|
| 7.1 | La lista de precios cubre sólo 2025, trae tres tipos de alimento (engorda 100, engorda 200 y pigmentado) y **no trae kilos comprados**: el promedio mensual sólo puede ser simple | Medido | archivo de costos |
| 7.2 | Todos los precios vienen en **CLP**. El dólar de mindicador.cl no hace falta para convertir precios; se usa para expresar los resultados en USD | Medido | archivo de costos |
| 7.3 | 3 de las 36 filas de precios son ilegibles (tipo, mes o precio) | Medido | `cobertura.csv` |
| 7.4 | Valorizar el alimento según el tipo que le corresponde a cada pez por su peso, en vez de un precio único, baja los pesos por kg en 2,5 % y no cambia nada en kilos | Medido | `sensibilidad_definiciones.csv` (fila 2) |

## 8. Formatos y calidad

| # | Hallazgo | Tipo | Dónde se ve |
|---|---|---|---|
| 8.1 | Las fechas vienen en varios formatos dentro de una misma columna (`2025-11-20`, `20/11/2025`, `24/12/2024`) | Medido | las tres fuentes |
| 8.2 | Los números mezclan punto de miles y coma decimal (`262.577` son 262.577 kilos; `964,00` son 964 pesos) | Medido | las tres fuentes |
| 8.3 | Hay 138 registros duplicados de jaula y día (0,99 % del registro diario) | Medido | `cobertura.csv` |
| 8.4 | **Cobertura: queda fuera el 1,48 % de los registros jaula-día** (0,99 % duplicados y 0,49 % posteriores a la cosecha) | Medido | `cifras.json` |

## Preguntas abiertas para la contraparte

1. ¿El SRS del centro Reloncaví afectó sólo a las jaulas 1 a 4 o al centro completo? (hallazgos 3.3 a 3.5)
2. ¿Qué son los registros diarios posteriores a la cosecha de una jaula? (6.4)
3. ¿Por qué sanidad declara miles de muertes en tres eventos donde la operación diaria no muestra ningún aumento? (3.9)
