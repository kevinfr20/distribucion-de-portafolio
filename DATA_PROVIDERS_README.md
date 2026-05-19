# Documentación: BVLDataProvider con Fallback a CSV

## 📋 Descripción General

Este módulo implementa un **Sistema de Obtención de Datos Robusto y Tolerante a Fallos** para la Bolsa de Valores de Lima (BVL). El sistema intenta obtener datos históricos desde la API de BVL y, en caso de fallo, carga automáticamente los datos desde archivos CSV locales como respaldo.

### Ventajas del Diseño

✅ **Tolerancia a Fallos**: Si la API falla (red, servidor, API key), el sistema automáticamente usa CSV  
✅ **Transparencia**: El cliente (optimizador) no necesita conocer el mecanismo de fallback  
✅ **Logging Detallado**: Cada paso se registra para auditoría y debugging  
✅ **Validación Automática**: Los datos se validan antes de usarse  
✅ **Extensible**: Fácil añadir nuevos proveedores (Web scraping, BD, etc.)  

---

## 🏗️ Arquitectura

---

## 📁 Estructura de Archivos

proyecto/ │ ├── data_providers/ │ ├── init.py # Inicialización del paquete │ ├── base_provider.py # Clase abstracta (interfaz) │ ├── local_csv_provider.py # Proveedor de CSV │ └── bvl_data_provider.py # Proveedor de BVL (principal) │ ├── data/ │ └── bvl_fallback/ # Carpeta de respaldo de CSVs │ ├── ALICORC1.csv │ ├── VOLCABC1.csv │ └── UNACEMC1.csv │ ├── examples/ │ └── example_usage.py # Ejemplos de uso │ ├── tests/ │ └── test_bvl_provider.py # Suite de pruebas unitarias │ └── README.md


---

## 🚀 Guía de Uso

### 1. Instalación de Dependencias

```bash
pip install pandas requests python-dateutil

2. Uso Básico

from datetime import datetime
from data_providers import BVLDataProvider

# Inicializar el proveedor
provider = BVLDataProvider(
    api_base_url="https://api.bvl.com.pe/v1",
    api_timeout=30,
    fallback_dir="./data/bvl_fallback/",
)

# Obtener datos (intenta API, luego CSV)
df = provider.get_historical_data(
    ticker="ALICORC1",
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2026, 5, 19),
)

print(df.head())

Salida esperada:

             Open  High   Low  Close  Volume
Date                                          
2025-01-01  1.69  1.70  1.68   1.68   19052
2025-01-02  1.70  1.71  1.69   1.70   20000
...

📊 Estructura del CSV
El CSV debe tener el siguiente formato (separador ;):

Fecha de cotización;Apertura;Cierre;Máximo;Mínimo;Promedio;Cantidad negociada;Monto negociado (S/);Fecha anterior;Cierre anterior corregido
15/05/2026;1.69;1.68;1.69;1.68;1.6952902582406046;19052;32298.67;14/05/2026;1.72
14/05/2026;1.72;1.72;1.72;1.72;1.7241912287633345;12655;21819.64;13/05/2026;1.702

Columnas Mapeadas:

CSV Original	Estándar	Tipo
Fecha de cotización	Date	datetime
Apertura	Open	float
Máximo	High	float
Mínimo	Low	float
Cierre	Close	float
Cantidad negociada	Volume	int


🔧 Componentes Principales

1. BaseDataProvider (Interfaz Abstracta)
Define el contrato que todos los proveedores deben cumplir.

from data_providers import BaseDataProvider
import pandas as pd
from datetime import datetime

class CustomProvider(BaseDataProvider):
    def get_historical_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        # Implementación
        pass

    def validate_data(self, data: pd.DataFrame, ticker: str) -> bool:
        # Validación
        pass

2. LocalCSVProvider (Respaldo Local)
Carga datos desde archivos CSV locales.

from data_providers import LocalCSVProvider
from datetime import datetime

csv_provider = LocalCSVProvider(
    fallback_dir="./data/bvl_fallback/",
    encoding="utf-8",
    delimiter=";",
)

# Verificar si existe archivo
if csv_provider.file_exists("ALICORC1"):
    df = csv_provider.load_historical_data(
        ticker="ALICORC1",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2026, 5, 19),
    )
    print(df)

Métodos clave:

Método	Descripción
file_exists(ticker)	Verifica si existe el CSV para un ticker
get_csv_path(ticker)	Retorna la ruta del CSV
load_historical_data(...)	Carga datos del CSV
save_historical_data(...)	Guarda datos en CSV

3. BVLDataProvider (Orquestador Principal)
Implementa la lógica de tolerancia a fallos.

from data_providers import BVLDataProvider
from datetime import datetime

provider = BVLDataProvider(
    api_base_url="https://api.bvl.com.pe/v1",
    api_timeout=30,
    api_key="tu_api_key_aqui",  # Opcional
    fallback_dir="./data/bvl_fallback/",
)

# Flujo automático: API → CSV → Error
try:
    df = provider.get_historical_data(
        ticker="ALICORC1",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2026, 5, 19),
    )
except ValueError as e:
    print(f"Error: {e}")

Métodos principales:

Método	Descripción
get_historical_data(...)	Obtiene datos (API + fallback)
validate_data(df, ticker)	Valida el formato del DataFrame
_fetch_from_api(...)	Intenta obtener de la API
_standardize_api_response(df)	Estandariza respuesta de API

🛡️ Manejo de Errores
El sistema maneja los siguientes escenarios:

1. API No Disponible (Timeout)

try:
    df = provider.get_historical_data(...)
except TimeoutError:
    # Automáticamente intenta CSV
    pass

2. API Key Inválida

# Registra en log y intenta CSV
logger.warning("API key inválida o expirada (401)")

3. CSV No Existe

raise FileNotFoundError(
    f"Archivo CSV no encontrado para {ticker}: {csv_path.absolute()}"
)

4. Ambos Fallan

raise ValueError(
    f"No se pudo obtener data de la API ni del respaldo CSV local "
    f"para el ticker {ticker}"
)

📝 Logging
El sistema usa logging para registrar todos los eventos:

import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bvl_provider.log"),
    ],
)

Ejemplo de salida:

2026-05-19 14:32:10 - data_providers.bvl_data_provider - INFO - BVLDataProvider inicializado
2026-05-19 14:32:11 - data_providers.bvl_data_provider - INFO - Obteniendo datos históricos para ALICORC1 desde 2025-01-01 hasta 2026-05-19
2026-05-19 14:32:12 - data_providers.bvl_data_provider - WARNING - Error de conectividad al intentar obtener datos de la API
2026-05-19 14:32:12 - data_providers.bvl_data_provider - INFO - Intentando cargar datos desde respaldo CSV para ALICORC1...
2026-05-19 14:32:12 - data_providers.local_csv_provider - INFO - Cargando datos históricos desde CSV
2026-05-19 14:32:13 - data_providers.bvl_data_provider - INFO - Datos cargados exitosamente desde CSV para ALICORC1

✅ Validación de Datos
El sistema valida automáticamente:

✓ DataFrame no vacío
✓ Todas las columnas presentes
✓ Tipos de datos correctos
✓ Índice es DatetimeIndex
✓ No hay valores NaN críticos

df = provider.get_historical_data(...)
provider.validate_data(df, "ALICORC1")  # Lanza ValueError si no es válido

🧪 Pruebas Unitarias
Ejecutar la suite de pruebas:

python -m pytest tests/test_bvl_provider.py -v

O con unittest:
python tests/test_bvl_provider.py

Cobertura de pruebas:
TestLocalCSVProvider
├── test_init_creates_directory
├── test_get_csv_path
├── test_get_csv_path_uppercase
├── test_file_exists_nonexistent
├── test_standardize_columns
├── test_standardize_columns_missing_column
├── test_standardize_dtypes
└── test_create_empty_dataframe

TestBVLDataProvider
├── test_init
├── test_required_columns
├── test_validate_data_valid
├── test_validate_data_empty
├── test_validate_data_missing_column
├── test_validate_data_invalid_index
├── test_fetch_from_api_timeout
├── test_fetch_from_api_connection_error
├── test_get_historical_data_fallback_to_csv
└── test_get_historical_data_api_and_csv_fail

TestIntegration
└── test_full_workflow_csv_fallback


 Casos de Uso
Caso 1: Obtener Datos con Fallback Automático

from datetime import datetime, timedelta
from data_providers import BVLDataProvider

provider = BVLDataProvider()

# Obtener últimos 30 días
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

df = provider.get_historical_data(
    ticker="ALICORC1",
    start_date=start_date,
    end_date=end_date,
)

# Usar para optimización de portafolio
returns = df['Close'].pct_change()
volatility = returns.std()
print(f"Volatilidad: {volatility:.4f}")

Caso 2: Verificar Disponibilidad de Datos

csv_provider = provider.csv_provider

if csv_provider.file_exists("ALICORC1"):
    print("✓ Datos disponibles en respaldo CSV")
else:
    print("✗ No hay respaldo para ALICORC1")

Caso 3: Guardar Datos Nuevos como Respaldo

# Después de obtener datos de la API
df_from_api = provider._fetch_from_api(...)
provider.csv_provider.save_historical_data("ALICORC1", df_from_api)

📈 Performance
Tiempos de Carga
Fuente	Tiempo Aprox.
API de BVL	0.5 - 2 segundos
CSV Local	0.1 - 0.5 segundos
Fallback (API→CSV)	1 - 3 segundos

Uso de Memoria

import pandas as pd

# Para 2000 registros
df = pd.DataFrame(
    {col: [0.0] * 2000 for col in ["Open", "High", "Low", "Close"]}
)
df["Volume"] = [0] * 2000
df.set_index(pd.date_range("2000-01-01", periods=2000), inplace=True)

print(df.memory_usage(deep=True).sum() / 1024)  # ≈ 80 KB

🚨 Troubleshooting
Problema: "No se pudo obtener data de la API ni del respaldo CSV"
Causas posibles:

API de BVL no disponible
CSV no existe en ./data/bvl_fallback/
CSV está corrupto
Ticker incorrecto
Soluciones:

# 1. Verificar connectividad
import requests
requests.get("https://api.bvl.com.pe/v1", timeout=5)

# 2. Verificar archivo CSV
from pathlib import Path
csv_path = Path("./data/bvl_fallback/ALICORC1.csv")
print(csv_path.exists())

# 3. Validar CSV
import pandas as pd
df = pd.read_csv(csv_path, delimiter=";")
print(df.head())

# 4. Verificar ticker (debe ser mayúsculas)
print("ALICORC1".upper())

Problema: "Tipo de dato no óptimo"
Solución: El sistema automáticamente convierte los tipos, pero puedes validar manualmente:

provider.validate_data(df, "ALICORC1")  # Lanza advertencia si hay tipos incorrectos

🔐 Seguridad
API Key: Guardar en variables de entorno, no en código
Validación: Todos los datos se validan antes de usarse
Logging: Sensible (no registra datos sensibles)

import os
# Usar variable de entorno
api_key = os.getenv("BVL_API_KEY")
provider = BVLDataProvider(api_key=api_key)

📚 Referencias
Documentación de Pandas
Requests HTTP Library
Python Logging
Design Patterns: Fallback/Failover

📄 Licencia
Este código es parte del proyecto "Gestionar y diversificar un portafolio de acuerdo a su data histórica y optimización respecto a su rentabilidad y riesgo".

👨‍💻 Autor
Software Engineer
Fecha: 2026-05-19

Última actualización: 2026-05-19
Estado: ✅ Producción
