# Prototipo — AquaFiordo, Grupo 10

Tablero en Tableau Desktop (2025.2+) que responde: ¿qué parte del sobrecosto del centro
con más costo se ataca con alimentación y cuál con sanidad, y cuánto vale cada una?

## Abrir
Abrir `PrototipoFinal.twbx` (empaquetado) y pasar al dashboard **Screen**. Presentar: Dashboard → Presentation Mode.

## Actualizar los datos
Las tablas que lee el tablero (`prototipo/datos/*.csv`, no versionadas) las escribe `entrega2.ipynb` al final de
cada corrida, solo si pasan las pruebas que bloquean:

```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 entrega2.ipynb
```

Luego, en Tableau: Datos → Actualizar todos los orígenes (F5). El `.twbx` lleva su propia copia; para actualizarlo hay
que volver a empaquetarlo (File → Export Packaged Workbook).
`exportar_datos_tableau.py` es el script anterior (corre `entrega1.ipynb`); queda solo como referencia.

## Resultado esperado
Centro Reloncaví, CLP 729 MM de sobrecosto; R = 1,74 vs 1,24; 54 % eficiencia (403 MM) /
39 % evento sanitario (282 MM) / 6 % mortalidad normal (44 MM). Cobertura: 1,48 % excluido.

## Regla
Solo Tableau Desktop local: no publicar en Tableau Public / Cloud / Server.
