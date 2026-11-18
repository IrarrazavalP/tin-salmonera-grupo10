# Salmonera · Grupo 10 (S3) · IIC3752 Entrega 2

Cadena de datos y prototipo que responden la pregunta de la gerencia:

> En el centro con más costo, ¿la causa es la mortalidad de un evento sanitario, un FCR peor, o ambas? ¿Se pueden separar?

Se integran las cuatro fuentes del caso (SQLite, CSV, JSON y la API de mindicador.cl) en una tabla de **una fila por jaula y día** y se calcula cuántos kg de alimento usa cada centro por kg cosechado (**R**), repartido en tres partes que suman el total: peces cosechados (eficiencia), muertos en un evento sanitario y muertos por mortalidad normal.

## Qué hay en el repositorio

| Ruta | Qué es |
|---|---|
| `entrega2.ipynb` | **Cadena de la Entrega 2**, por capas (cruda → depurada → modelo → consumo), con pruebas de calidad en cada corrida |
| `metrica.py` | **Capa semántica:** la métrica R y sus tres partes, la brecha, los pesos y las 9 definiciones alternativas (fórmulas F5 a F15), definidas una sola vez; `entrega2.ipynb` la importa y el informe y el prototipo leen lo que escribe con ella |
| `calidad.py` | Las 34 pruebas de calidad que corre `entrega2.ipynb` (qué verifica cada una y si avisa o bloquea) |
| `entrega1.ipynb` | Cadena de la Entrega 1, tal como se entregó (no se modifica) |
| `PrototipoFinal.twbx` | **Prototipo en Tableau, empaquetado** (con su copia de las tablas): se abre sin más, en cualquier computador con Tableau Desktop |
| `prototipo/` | Versión en vivo del prototipo (`PrototipoFinal-vivo.twb`), el script que arma el `.twbx` y la carpeta `datos/` que escribe `entrega2.ipynb`; ver `prototipo/README.md` |
| `figuras/` | Las 5 visualizaciones del informe (las regenera cada corrida) |
| `data/` | Aquí van los 3 archivos del caso (no se suben) y `data/cache/`, la copia guardada del dólar |
| `docs/` | Ficha de la métrica, hallazgos, bitácora de supuestos, evidencia y recomendaciones, declaración de uso de IA |
| `requirements.txt` | Versiones con las que se reproducen las cifras (Python 3.11) |

## Cómo reproducirlo

Requisitos: Python 3.11 o superior e internet (consulta a mindicador.cl; si falla, se usa la copia de `data/cache/`).

```bash
git clone <url de este repositorio>
cd tin-salmonera-grupo10
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Los datos del caso **no están en el repositorio** (son de la empresa). Déjalos en `data/` con estos nombres:

```
data/origen_acuicultura.sqlite
data/origen_costos_alimento.csv
data/origen_eventos_sanitarios.json
```

Un solo comando, desde la raíz del repositorio:

```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 entrega2.ipynb
```

**Cuánto demora:** instalar los paquetes, ≈ 1,5 min la primera vez. El comando, entre 45 s y 1,5 min (la primera corrida en un ambiente nuevo es la más lenta); de eso, la cadena en sí son 15–40 s. Si la API del dólar no responde, cada año consultado puede sumar hasta 20 s de espera antes de pasar a la copia guardada.

### Qué deja la corrida

| Dónde | Qué | Cuándo se escribe |
|---|---|---|
| `results/` (17 archivos) | `cifras.json` (las cifras que cita el informe, incluida la cifra de referencia con su rango entre las 10 definiciones), 14 tablas (por centro, especie, lote, brecha, alternativas, sensibilidad, eventos, cobertura, hechos jaula-día…), `calidad.csv` y `estado_corrida.json` | Solo si pasan todas las pruebas que bloquean |
| `figuras/` | Las 5 figuras del informe | Junto con `results/` |
| `prototipo/datos/` (10 tablas) | Lo que lee el tablero de Tableau | Después de `results/`, y solo si pasa la prueba M-12 |
| `entrega2.ipynb` | El mismo notebook con las salidas de esta corrida (`--inplace`) | Siempre |

`results/` y `prototipo/datos/` no se suben al repositorio: se generan con el comando.

### Cómo saber si salió bien

1. El comando termina sin error y la última celda dice `Pruebas de la corrida: … 0 fallas`.
2. `results/estado_corrida.json` dice `"resultado": "publicada"` y `"prototipo": {"actualizado_en_esta_corrida": true, …}`.
3. `results/cifras.json` reproduce las cifras del informe:

| Cifra | Valor esperado |
|---|---|
| Centro más caro | 1 (Reloncaví) |
| R centro / R resto / brecha | 1,745 / 1,238 / 0,507 kg/kg |
| Aporte a la brecha (eficiencia / evento / basal) | 54,4 / 39,4 / 6,2 % |
| Sobrecosto | CLP 403 + 282 + 44 = 729 MM |
| Cobertura | 1,48 % de los registros jaula-día excluido (207 de 13.978) |

La prueba M-10 avisa sola si alguna de estas cifras se aleja de la Entrega 1.

## Pruebas de calidad

Corren en cada ejecución, sobre los datos reales, y dejan su resultado en `results/calidad.csv`:

- **13 por fuente (F-01 a F-13):** el SQLite, el CSV y el JSON existen y tienen la forma esperada; fechas y números legibles; precios para cada mes; eventos dentro del período; respuesta válida de la API.
- **9 de la tabla de hechos (H-01 a H-09):** una fila por (lote, fecha), sin huérfanos, una cosecha por lote, rangos válidos, fechas dentro del período, precio para cada jaula-día.
- **12 de la métrica y las salidas (M-01 a M-12):** las tres partes suman R y el 100 %, la brecha y los pesos se reparten sin residuo, no se pierden registros, cobertura y completitud, cifras iguales a la E1, y lo que leen el informe (M-08) y el tablero (M-12) es el mismo número.

Cada prueba **bloquea** o **avisa**:

- **Bloquea:** la corrida se detiene y `results/` conserva la última versión publicada; `estado_corrida.json` dice `"bloqueada"` y en qué etapa. Si la que falla es M-12, `results/` ya está publicado pero `prototipo/datos/` conserva la versión anterior, y `estado_corrida.json` lo registra.
- **Avisa:** la corrida sigue y el aviso queda registrado. Hoy el único aviso esperable es F-13 cuando mindicador.cl no responde.

## Arquitectura (cómo está implementada)

- **Capas:** cruda (`data/`, los archivos del caso sin modificar y la copia de la API en `data/cache/`) → depurada y modelo (en memoria, dentro del notebook) → semántica (`metrica.py`) → consumo (`results/`, `figuras/`, `prototipo/datos/`).
- **La métrica se define una sola vez, en `metrica.py`:** el notebook arma la tabla jaula-día (fórmulas F1 a F4), se la entrega con `metrica.configurar(...)` y llama a sus funciones; no hay fórmulas de la métrica repetidas en el notebook ni en Tableau. Ahí también está la regla del 5 % con que se dice si las dos fuentes de mortalidad (operación diaria y sanidad) calzan.
- **Se transforma después de cargar (ELT):** los archivos de origen nunca se modifican; toda limpieza y corrección se hace en el notebook y queda contada en `results/cobertura.csv`.
- **Carga completa en cada corrida:** se recalcula todo desde los archivos de origen y se reemplazan las salidas. Dos corridas seguidas dan el mismo `cifras.json` y la misma tabla de hechos; en cada corrida se verifica que no haya filas duplicadas (H-01) ni registros perdidos (M-09).
- **Si la API del dólar falla:** se usa la última copia guardada en `data/cache/`. Si no hay copia, las cifras en kg y CLP salen completas, las de USD dicen «no disponible» y el pie del prototipo lo declara.
- **Acuerdo de servicio** (se mide en cada corrida y queda en `estado_corrida.json`): frescura mensual, a más tardar 15 días después del cierre de mes; completitud ≥ 98 % de los registros jaula-día; 100 % de las pruebas que bloquean y ≥ 95 % del total en verde. Dueño: Gerente de Producción; corre la cadena: Analista de control de gestión (cargos propuestos por el grupo).

## La métrica

```
R = alimento total (kg) ÷ kg cosechados = R_cosecha + R_evento + R_basal

R_cosecha = alimento de los peces que llegaron a la cosecha          → eficiencia (FCR)
R_evento  = alimento de los peces muertos en un evento (exceso sobre la basal)
R_basal   = alimento de los peces muertos por mortalidad normal
```

Las diferencias entre el centro más caro y el resto se reparten entre las tres partes sin residuo. Las fórmulas están en `metrica.py` (`DECISIONES` trae las 9 decisiones de definición con su valor principal y `ALTERNATIVAS`, las que muestra el prototipo). El FCR bruto que se reporta al directorio (alimento ÷ biomasa final) se llama «FCR bruto» en el informe y en el tablero, y `R_bruto_gerencia` en el código. Las decisiones de definición y sus alternativas están en `docs/ficha_metrica.md`; cada supuesto, en `docs/bitacora.md`.

## Prototipo

Requiere **Tableau Desktop 2025.2 o superior**, solo local: no publicar en Tableau Public, Cloud ni Server (los datos son de la empresa). Sin Tableau Desktop: el informe trae pantallazos de las dos pantallas (*Screen* y *Definition*).

- `PrototipoFinal.twbx` (en la raíz) es el libro empaquetado, con su propia copia de las tablas: se abre sin más, en cualquier computador. Es una foto de la corrida con la que se empaquetó.
- `prototipo/PrototipoFinal-vivo.twb` lee en vivo `prototipo/datos/`, que escribe `entrega2.ipynb` en la misma corrida.

Cómo abrirlo, actualizarlo y volver a empaquetarlo: `prototipo/README.md`.

> Nota: algunos documentos de `docs/` (`hallazgos.md`, `revision_notebook_martin.md`) son de la Entrega 1 y mencionan el comando `python -m salmonera`, que ya no existe; la cadena vigente es `entrega2.ipynb`.
