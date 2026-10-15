# Ficha de la métrica: pendientes e inconsistencias

Notas internas del grupo, no van al informe. Acompañan a [ficha_metrica.md](ficha_metrica.md).

## Pendiente antes de entregar

1. **[POR CONFIRMAR]** Acordar con el grupo la decisión 9, que es la que más mueve la respuesta.
2. **[POR CONFIRMAR]** Validar la forma exacta de la alternativa de la decisión 3 y la de la decisión 1.
3. **[POR CONFIRMAR]** Confirmar los cortes de peso de 1,5 y 4 kg de la decisión 2.
4. **[POR CONFIRMAR]** Correr el notebook de cero en un ambiente limpio y comprobar que salen estas mismas cifras.


## Inconsistencias con las otras partes del informe

Estas diferencias hay que resolverlas antes de que Pedro integre el informe.

### Con el código en `main` (componente B)

1. **`main` no produce las cifras de esta ficha.** El paquete `salmonera/` de `main` implementa la métrica de la versión 2: FCR biológico, FCR económico y costo en CLP por kg ganado. La métrica de la versión 3 sólo está en `entrega1.ipynb` de la rama `hallazgos`, que no está fusionada. Si el informe enlaza `main`, ninguna cifra de esta ficha se reproduce, y la regla del grupo dice que entonces B vale cero.
2. **El README de `main` describe la métrica antigua** y una decisión de basal por etapa como principal, que la versión 3 cambió a global.

### Con la sección E de Martín (`docs/Evidencia_y_recomendacion.md`)

3. **Usa la métrica antigua y otras cifras.** E dice que el centro 1 cuesta 2.186,5 CLP por kg ganado; con R, son 1.959 CLP por kg cosechado. E dice que el resto promedia unos 1.540 CLP/kg; esa cifra no sale del código de la versión 3.
4. **El reparto de la brecha no coincide.** E dice 57,9 % por FCR y 25,8 % por el evento; esta ficha dice 54,4 % por eficiencia, 39,4 % por el evento y 6,2 % basal.
5. **Habla de FCR biológico de 1,54 y FCR económico de 1,94.** Esas magnitudes no existen en la métrica R. La cifra comparable es R_cosecha del centro 1, de 1,431.
6. **El costo del evento no coincide.** E dice 218.006.017 CLP de pérdida por el brote; el código de la versión 3 da 282 millones de CLP de sobrecosto por el evento frente al resto.
7. **La cobertura no coincide.** E dice 0,99 % de registros excluidos; el código de la versión 3 da 1,48 %, porque también excluye los registros posteriores a la cosecha.
8. **Los gráficos de E son de la versión 2.** Muestran costo en CLP por kg ganado y FCR biológico y económico. Habría que reemplazarlos por los del notebook: R por centro en tres partes, brecha, mortalidad en torno a eventos, R_cosecha por centro y especie, y % del alimento perdido.
9. **E atribuye el costo del evento a la «detección tardía».** Los datos muestran que la mortalidad sube el mismo día que sanidad declara el inicio, así que no hay evidencia de rezago en la detección.

### Con el mandato de Luz María (A, `AquaFiordo.docx`)

10. **La ventana del evento quedó «N por fijar».** Con los datos se fijó N = 0. El mandato debería decirlo, o la ficha y el mandato no coinciden.
11. **La basal se define distinto.** El mandato dice «el promedio de la mortalidad diaria»; el código usa Σ muertos ÷ Σ población, que pondera por tamaño de jaula. Conviene usar en el mandato la misma redacción que F5.
12. **Falta la decisión 9.** El mandato no menciona que un evento alcanza a todo el centro, y es la decisión que más mueve la respuesta.
13. **La tabla de hallazgos no tiene ninguno «medido».** La rúbrica pide marcar verbalizado, medido o inferido. Varios ya están medidos: por ejemplo, «un pez que muere tarde representa más alimento perdido» está marcado como inferido, y el código lo mide en 4,9 kg contra 2,3 kg.
14. **El plan de trabajo dice que el acumulado parte en la siembra** (F3), pero el código parte en el primer registro, el 01-01-2025. El mandato no lo menciona; si el informe cita el plan, hay que corregirlo.

### Con el archivo de hallazgos de Pedro (`docs/hallazgos.md`, rama `hallazgos`, 10-10)

15. **Tiene cifras de una corrida anterior.** Dice 55 / 39 / 6, 731 millones, R del resto 1,23, precio por peso −2,5 % y alternativa 3 +0,9 %. La salida actual del notebook dice 54 / 39 / 6, 729 millones, 1,24, −2,1 % y +11,7 %. Esta ficha usa la salida del notebook. La bitácora de esa rama tiene las mismas cifras antiguas.
