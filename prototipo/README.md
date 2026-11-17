# Prototipo — AquaFiordo, Grupo 10

Tablero en Tableau Desktop (2025.2+) que responde: ¿qué parte del sobrecosto del centro
con más costo se ataca con alimentación y cuál con sanidad, y cuánto vale cada una?

## Qué hay aquí y en la raíz

El libro empaquetado `PrototipoFinal.twbx` está en la **raíz del repositorio** (no necesita la carpeta `datos/`: lleva su propia copia). Esta carpeta guarda el `.twb` vivo, las tablas y el script que empaqueta.

| Archivo | Qué es | Cuándo usarlo |
|---|---|---|
| `../PrototipoFinal.twbx` (raíz) | **Libro empaquetado**: el tablero con su propia copia de las tablas (`Data/datos/`), con rutas relativas | **Para abrir y presentar** (también en otro computador). Es una foto de la corrida con que se empaquetó |
| `PrototipoFinal-vivo.twb` | El mismo tablero, **conectado en vivo** a `prototipo/datos/` | Para ver los datos nuevos tras correr el notebook. Guarda rutas absolutas del computador donde se guardó por última vez |
| `datos/` | Las 10 tablas que escribe `entrega2.ipynb` (CSV). **No se versionan** | Se regeneran al correr el notebook |
| `empaquetar_twbx.py` | Arma `PrototipoFinal.twbx` en la raíz desde el `.twb` vivo y `datos/` | Tras cada corrida, si se quiere un `.twbx` con los datos al día |

De las 10 tablas, el tablero usa 8. `cobertura.csv` y `pruebas_calidad.csv` quedan como detalle: la cobertura y el conteo de pruebas llegan al tablero por `meta.csv` (pie de la pantalla).

## Abrir y presentar
Abrir `PrototipoFinal.twbx` (raíz del repo) y pasar al dashboard **Screen**. Para presentar: Dashboard → Presentation Mode.
No necesita nada más ni conexión a internet.

## Actualizar con una nueva corrida
1. Correr la cadena desde la raíz del repositorio:
   ```bash
   jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 entrega2.ipynb
   ```
   Escribe `prototipo/datos/` al final, después de publicar `results/`, y solo si pasa la prueba **M-12** (las tablas
   del tablero muestran el mismo número que `results/cifras.json`, que es lo que cita el informe). Si M-12 falla o
   esa celda da error, `prototipo/datos/` conserva la versión anterior y `results/estado_corrida.json` lo registra en
   `"prototipo"`.
2. **Ver los datos nuevos en vivo:** abrir `PrototipoFinal-vivo.twb` y, en el dashboard, Data → Refresh All
   Data Sources. Cada origen debe estar en **Live** (con Extract se queda con una copia congelada).
3. **Actualizar el empaquetado:** `python3 prototipo/empaquetar_twbx.py` regenera `PrototipoFinal.twbx` en la raíz con
   las tablas de la última corrida y el diseño de `PrototipoFinal-vivo.twb`. Si se cambia el diseño del tablero,
   guardarlo primero en el `.twb` vivo; si no, el `.twbx` nuevo no lo tendrá.

> El `.twbx` **no se actualiza solo**: lee su copia interna. Para que el viernes muestre «los datos de la última
> corrida», correr el notebook y regenerar el `.twbx` justo antes.

## En otro computador (por ejemplo, la corrida desde cero)
El `.twbx` de la raíz abre en cualquier computador. El `.twb` vivo, en cambio, apunta a la carpeta `prototipo/datos/`
del computador donde se guardó por última vez: al abrirlo en otro, Tableau avisa que no encuentra los archivos y
hay que indicarle la carpeta `prototipo/datos/` de este repositorio (después de haber corrido el notebook). Tras
ese cambio, `empaquetar_twbx.py` sigue funcionando: reemplaza cualquier ruta que termine en `/datos` por la copia
interna del paquete.

Si `mindicador.cl` no responde se usa la copia de `data/cache/`; sin copia para ese año, el tablero muestra solo
pesos y lo declara en el pie (la prueba F-13 avisa y no bloquea).

## Resultado esperado
Centro Reloncaví, CLP 729 MM de sobrecosto; R = 1,74 vs 1,24; 54 % eficiencia (403 MM) /
39 % evento sanitario (282 MM) / 6 % mortalidad normal (44 MM). Cobertura: 1,48 % excluido.
Pie: 34 pruebas de calidad, todas en verde salvo F-13 cuando no hay dato del dólar.

## Regla
Solo Tableau Desktop local: no publicar en Tableau Public / Cloud / Server (los datos del caso son de la
empresa y no se pueden subir a terceros).
