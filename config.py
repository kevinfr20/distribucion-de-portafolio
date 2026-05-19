"""
Módulo: config.py
Descripción: Configuración centralizada del proyecto.
Autor: Software Engineer
Fecha: 2026-05-19
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ===========================
# PATHS
# ===========================

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.absolute()

# Directorios
DATA_DIR = PROJECT_ROOT / "data"
FALLBACK_DIR = DATA_DIR / "bvl_fallback"
LOGS_DIR = PROJECT_ROOT / "logs"

# Crear directorios si no existen
FALLBACK_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ===========================
# BVL API CONFIGURATION
# ===========================

BVL_API_BASE_URL = os.getenv(
    "BVL_API_BASE_URL",
    "https://api.bvl.com.pe/v1"
)

BVL_API_KEY = os.getenv("BVL_API_KEY", None)

BVL_API_TIMEOUT = int(os.getenv("BVL_API_TIMEOUT", "30"))

BVL_API_RETRIES = int(os.getenv("BVL_API_RETRIES", "3"))

# ===========================
# CSV CONFIGURATION
# ===========================

CSV_ENCODING = "utf-8"
CSV_DELIMITER = ";"

CSV_DATE_FORMAT = "%d/%m/%Y"

# ===========================
# LOGGING CONFIGURATION
# ===========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LOG_FILE = LOGS_DIR / "bvl_provider.log"

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB

LOG_BACKUP_COUNT = 5

# ===========================
# OPTIMIZATION CONFIGURATION
# ===========================

# Rango de fechas por defecto para obtener datos históricos
DEFAULT_LOOKBACK_DAYS = 365

# Mínimo de registros requeridos para análisis
MIN_REQUIRED_RECORDS = 30

# ===========================
# VALIDATION CONFIGURATION
# ===========================

# Columnas requeridas en datos históricos
REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]

# Tipos de datos esperados
EXPECTED_DTYPES = {
    "Open": ["float64", "float32"],
    "High": ["float64", "float32"],
    "Low": ["float64", "float32"],
    "Close": ["float64", "float32"],
    "Volume": ["int64", "int32"],
}

# Tolerancia para validación de precios (no deben variar >X% en un día)
MAX_DAILY_CHANGE_PCT = 50.0  # 50%

# ===========================
# CACHE CONFIGURATION
# ===========================

ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

# ===========================
# DEBUG
# ===========================

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

VERBOSE_LOGGING = os.getenv("VERBOSE_LOGGING", "False").lower() == "true"
