# Prototipo — AquaFiordo, Grupo 10

Tablero en Tableau Desktop (2025.2+) que responde: ¿qué parte del sobrecosto del centro
con más costo se ataca con alimentación y cuál con sanidad, y cuánto vale cada una?

## Qué hay aquí y en la raíz

El libro empaquetado `PrototipoFinal.twbx` está en la **raíz del repositorio** (no necesita la carpeta `datos/`: lleva su propia copia). Esta carpeta guarda el `.twb` vivo, las tablas y los scripts.

| Archivo | Qué es | Cuándo usarlo |
|---|---|---|
| `../PrototipoFinal.twbx` (raíz) | **Libro empaquetado**: el tablero con su propia copia de las tablas (`Data/datos/`), con rutas relativas | **Para abrir y presentar** (también en otro computador). Es una foto de la última corrida |
| `PrototipoFinal-vivo.twb` | El mismo tablero, **conectado en vivo** a `prototipo/datos/` | Para ver los datos nuevos tras correr el notebook. Tiene rutas absolutas del computador donde se guardó |
| `datos/` | Las 10 tablas que lee el tablero (CSV). **No se versionan**: las escribe `entrega2.ipynb` | Se regeneran al correr el notebook |
| `empaquetar_twbx.py` | Arma `PrototipoFinal.twbx` (en la raíz) desde el `.twb` vivo y `datos/` | Tras cada corrida, si se quiere un `.twbx` con datos al día |
| `exportar_datos_tableau.py` | Script anterior (corre `entrega1.ipynb`) | Solo como referencia: ya no se usa |

## Abrir y presentar
Abrir `PrototipoFinal.twbx` (raíz del repo) y pasar al dashboard **Screen**. Presentar: Dashboard → Presentation Mode.
No necesita nada más ni conexión a internet.

## Actualizar con una nueva corrida
1. Correr la cadena; escribe `prototipo/datos/` al final, justo después de publicar `results/` y solo si
   pasan las pruebas que bloquean:
   ```bash
   jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 entrega2.ipynb
   ```
2. **Ver los datos nuevos en vivo:** abrir `PrototipoFinal-vivo.twb` y, en el dashboard, Data → Refresh All
   Data Sources. Cada origen debe estar en **Live** (con Extract se queda con una copia congelada). Si Tableau
   no encuentra los archivos (por ejemplo, en otro computador), apuntarlo a `prototipo/datos/`.
3. **Actualizar el empaquetado:** `python3 prototipo/empaquetar_twbx.py` regenera `PrototipoFinal.twbx` con las
   tablas de la última corrida. (También se puede en Tableau: File → Export Packaged Workbook, desde el `.twb`.)

> El `.twbx` **no se actualiza solo**: lee su copia interna. Para que el viernes muestre «los datos de la última
> corrida», correr el notebook y regenerar el `.twbx` justo antes.

Si `mindicador.cl` no responde se usa la copia de `data/cache/`; sin copia para ese año, el tablero muestra solo
pesos y lo declara en el pie (la prueba F-13 avisa y no bloquea).

## Resultado esperado
Centro Reloncaví, CLP 729 MM de sobrecosto; R = 1,74 vs 1,24; 54 % eficiencia (403 MM) /
39 % evento sanitario (282 MM) / 6 % mortalidad normal (44 MM). Cobertura: 1,48 % excluido.

## Regla
Solo Tableau Desktop local: no publicar en Tableau Public / Cloud / Server (los datos del caso son de la
empresa y no se pueden subir a terceros).
