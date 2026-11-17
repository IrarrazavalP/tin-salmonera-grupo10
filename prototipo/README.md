# Prototipo — AquaFiordo, Grupo 10

Tablero en Tableau Desktop (2025.2+) que responde: ¿qué parte del sobrecosto del centro
con más costo se ataca con alimentación y cuál con sanidad, y cuánto vale cada una?

## Abrir
Abrir `Prototipo.twbx` (empaquetado) y pasar al dashboard **Screen**. Presentar: Dashboard → Presentation Mode.

## Regenerar las tablas
```bash
python3 prototipo/exportar_datos_tableau.py --repo .
```
Escribe `prototipo/datos/*.csv` (no versionados: son datos derivados del caso). Tarda unos segundos.
Si `mindicador.cl` no responde usa `data/cache/dolar.json`; sin caché el tablero muestra solo pesos y lo declara.

## Resultado esperado
Centro Reloncaví, CLP 729 MM de sobrecosto; R = 1,74 vs 1,24; 54 % eficiencia (403 MM) /
39 % evento sanitario (282 MM) / 6 % mortalidad normal (44 MM). Cobertura: 1,48 % excluido.

## Regla
Solo Tableau Desktop local: no publicar en Tableau Public / Cloud / Server.
