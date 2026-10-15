# D. Ficha de la métrica

**Responsable:** Felipe Arnolds. Todas las cifras salen del código del repositorio (`entrega1.ipynb`).

## Qué mide

La métrica **R** mide cuántos kilos de alimento se usaron por cada kilo de pez cosechado, y reparte ese alimento en tres partes que suman el total. Así separa las dos causas posibles del alza de costo: un FCR peor o la mortalidad de un evento sanitario.

```
R = alimento total ÷ kg cosechados = R_cosecha + R_evento + R_basal
```

| Parte | Qué es | Causa que representa |
|---|---|---|
| R_cosecha | Alimento que comieron los peces que llegaron a cosecha | Eficiencia (FCR) |
| R_evento | Alimento que ya habían comido los peces muertos en un evento, sólo el exceso sobre la mortalidad normal | Evento sanitario |
| R_basal | Alimento que ya habían comido los peces muertos por mortalidad normal | Mortalidad esperable |

| Campo | Definición |
|---|---|
| Numerador | Σ `alimento_kg` del lote, desde su primer registro hasta el día de su cosecha |
| Denominador | Kilos vivos cosechados del lote |
| Unidad | kg de alimento por kg cosechado. Cada parte también como % del alimento total |
| Grano | Se calcula por lote y se agrega sumando numeradores y denominadores, sin promediar razones |
| Filtros | Registros jaula-día válidos, sin duplicados y hasta la cosecha. Eventos de centros que existen en la base. Queda fuera el 1,48 % de los registros jaula-día |
| En pesos | Sólo al final: alimento × precio promedio mensual único, igual para todas las jaulas |
| Referencia | R bruto de la gerencia = alimento ÷ biomasa final |

## Cómo se calcula

Para cada lote, día a día:

1. **Alimento por pez:** a = `alimento_kg` ÷ (`poblacion` − `mortalidad_n`). Los muertos del día no comen.
2. **Alimento acumulado por pez hasta el día anterior:** A(d) = Σ a(t) para t < d.
3. **Mortalidad basal:** b = Σ muertos ÷ Σ población, en las jaulas-día fuera de toda ventana de evento. Vale 3,92 muertos por cada 10.000 peces al día.
4. **Muertes del día:** fuera de una ventana de evento, todas son basales. Dentro de una ventana, las basales son a lo más b × población y el resto es exceso del evento.
5. **Alimento perdido:** P_basal = Σ muertes basales × A(d) y P_evento = Σ muertes de evento × A(d).
6. **Alimento de los cosechados:** A_cosecha = alimento total − P_basal − P_evento.
7. **Partes de R:** R_x = A_x ÷ kg cosechados.
8. **Brecha:** ΔR = R(centro más caro) − R(resto), y el aporte de cada parte es ΔR_x ÷ ΔR.

## Resultado

| Parte | Centro 1 Reloncaví | Resto de los centros | Brecha | Aporte a la brecha |
|---|---|---|---|---|
| R_cosecha | 1,431 | 1,156 | 0,276 | **54 %** |
| R_evento | 0,200 | 0,000 | 0,200 | **39 %** |
| R_basal | 0,114 | 0,082 | 0,031 | **6 %** |
| **R total** | **1,745** | **1,238** | **0,507** | 100 % |

El centro 1 es el más caro y su sobrecosto se explica por ambas causas. Algo más de la mitad viene de una peor eficiencia de los peces cosechados, que aparece en sus tres especies. Casi 40 % viene del brote SRS de agosto a octubre de 2025. En pesos, el centro 1 gastó unos CLP 729 millones más en alimento que si rindiera como el resto.

## Decisiones de definición

Con ninguna alternativa cambia cuál es el centro más caro.

| # | Decisión elegida | Alternativa | Cuánto cambia |
|---|---|---|---|
| 1 | Denominador: kg cosechados | Biomasa ganada: cosechado − biomasa inicial | R del centro 1 sube 11,8 %. El reparto casi no cambia |
| 2 | Precio mensual único, promedio simple | Precio según el tipo de alimento por peso del pez | Los kilos no cambian. Los pesos por kg bajan 2,1 % |
| 3 | Pez muerto = alimento acumulado hasta el día anterior | Peso promedio × FCR del lote hasta ese día | Alimento perdido por eventos +11,7 %. Reparto 49 / 44 / 7 |
| 4 | Basal global | Basal por etapa del ciclo | Menos de 0,1 %. La mortalidad normal no varía por etapa |
| 5 | Ventana desde la fecha declarada, N = 0 | Desde 7 días antes | Alimento perdido por eventos +0,3 % |
| 6 | Eventos sin jaulas se atribuyen al centro | Excluirlos | Nada: esos eventos son de centros que no existen en la base |
| 7 | Exceso sobre la basal en la mortalidad diaria | Mortalidad declarada por sanidad | Alimento perdido por eventos +24 %. Evento 46 % de la brecha |
| 8 | La población registrada incluye a los muertos del día | La población ya viene sin ellos | 0,1 %. La elegida calza en el 100 % de los días y la otra en el 6 % |
| 9 | Un evento alcanza a todas las jaulas del centro | Sólo las jaulas que lista sanidad | Alimento perdido por eventos −34 %. Evento 26 % y basal 20 % de la brecha |

**Por qué la decisión 9 es la más importante.** Sanidad lista 4 jaulas en el brote del centro 1, pero las otras 2 tienen el mismo salto de mortalidad en las mismas fechas. Además, las muertes que declara sanidad, 62.478, calzan con el centro completo, 61.714, y no con las 4 jaulas, 41.078.

## Supuestos y límites

- **Un pez muerto comió lo mismo que el pez promedio vivo.** El pez enfermo come menos, así que el alimento perdido queda levemente sobreestimado.
- **El acumulado parte en el primer registro, el 01-01-2025.** Lo comido antes no está en los datos, así que el alimento perdido queda levemente subestimado.
- **Morir tarde cuesta más.** Un pez muerto en el brote del centro 1 ya había comido 4,9 kg de alimento, contra 2,3 kg en el brote del centro 2, que fue más temprano en el ciclo.
- **La eficiencia y el evento no son independientes.** Los sobrevivientes del brote probablemente comieron y crecieron peor. La métrica no puede decir cuánto de la peor eficiencia del centro 1 se debe al brote.
