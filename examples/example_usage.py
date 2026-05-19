"""
Módulo: example_usage.py
Descripción: Ejemplo de uso del BVLDataProvider con fallback a CSV.
Autor: Software Engineer
Fecha: 2026-05-19
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

from data_providers import BVLDataProvider, LocalCSVProvider

# Configurar logging para ver los detalles
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bvl_provider.log"),
    ],
)

logger = logging.getLogger(__name__)


def example_1_basic_usage():
    """
    Ejemplo 1: Uso básico del BVLDataProvider con API y fallback.
    """
    print("\n" + "=" * 80)
    print("EJEMPLO 1: Uso básico del BVLDataProvider")
    print("=" * 80)

    # Inicializar el proveedor
    provider = BVLDataProvider(
        api_base_url="https://api.bvl.com.pe/v1",
        api_timeout=30,
        fallback_dir="./data/bvl_fallback/",
    )

    # Definir fechas
    end_date = datetime(2026, 5, 19)
    start_date = datetime(2026, 1, 1)

    # Obtener datos (intentará API, luego CSV)
    try:
        df = provider.get_historical_data(
            ticker="UNACEMC1",
            start_date=start_date,
            end_date=end_date,
        )
        
        print(f"\n✓ Datos obtenidos exitosamente:")
        print(f"  - Ticker: UNACEMC1")
        print(f"  - Período: {start_date.date()} a {end_date.date()}")
        print(f"  - Registros: {len(df)}")
        print(f"  - Columnas: {list(df.columns)}")
        print(f"\nÚltimos 5 registros:")
        print(df.tail())

    except ValueError as e:
        print(f"\n✗ Error: {str(e)}")


def example_2_csv_provider_direct():
    """
    Ejemplo 2: Uso directo del LocalCSVProvider.
    """
    print("\n" + "=" * 80)
    print("EJEMPLO 2: Uso directo del LocalCSVProvider")
    print("=" * 80)

    # Inicializar el proveedor de CSV
    csv_provider = LocalCSVProvider(
        fallback_dir="./data/bvl_fallback/",
        encoding="utf-8",
        delimiter=";",
    )

    # Verificar si existe el archivo
    ticker = "UNACEMC1"
    csv_path = csv_provider.get_csv_path(ticker)

    print(f"\nBuscando archivo CSV:")
    print(f"  - Ruta esperada: {csv_path.absolute()}")
    print(f"  - Existe: {csv_provider.file_exists(ticker)}")

    if csv_provider.file_exists(ticker):
        try:
            # Cargar datos
            end_date = datetime(2026, 5, 19)
            start_date = datetime(2026, 1, 1)

            df = csv_provider.load_historical_data(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
            )

            print(f"\n✓ Datos cargados desde CSV:")
            print(f"  - Ticker: {ticker}")
            print(f"  - Registros: {len(df)}")
            print(f"  - Período: {df.index.min().date()} a {df.index.max().date()}")
            print(f"\nPrimeros 5 registros:")
            print(df.head())

        except Exception as e:
            print(f"\n✗ Error al cargar CSV: {str(e)}")
    else:
        print(f"\n✗ Archivo CSV no encontrado para {ticker}")


def example_3_validate_csv_format():
    """
    Ejemplo 3: Validar que el CSV cumpla con el formato esperado.
    """
    print("\n" + "=" * 80)
    print("EJEMPLO 3: Validación de formato del CSV")
    print("=" * 80)

    csv_provider = LocalCSVProvider(fallback_dir="./data/bvl_fallback/")
    provider = BVLDataProvider(fallback_dir="./data/bvl_fallback/")

    ticker = "UNACEMC1"
    
    if csv_provider.file_exists(ticker):
        try:
            # Cargar datos
            df = csv_provider.load_historical_data(
                ticker=ticker,
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2026, 12, 31),
            )

            # Validar
            is_valid = provider.validate_data(df, ticker)

            print(f"\n✓ Validación de formato:")
            print(f"  - Ticker: {ticker}")
            print(f"  - Válido: {is_valid}")
            print(f"\nEstructura del DataFrame:")
            print(f"  - Índice: {type(df.index).__name__} ({df.index.name})")
            print(f"  - Columnas: {list(df.columns)}")
            print(f"  - Tipos de datos:")
            for col, dtype in df.dtypes.items():
                print(f"    * {col}: {dtype}")

        except Exception as e:
            print(f"\n✗ Error: {str(e)}")


def example_4_error_handling():
    """
    Ejemplo 4: Manejo de errores y escenarios de fallo.
    """
    print("\n" + "=" * 80)
    print("EJEMPLO 4: Manejo de errores y escenarios de fallo")
    print("=" * 80)

    provider = BVLDataProvider(
        api_base_url="https://api.bvl.com.pe/v1",  # URL probablemente inválida
        api_timeout=5,  # Timeout corto para forzar error
        fallback_dir="./data/bvl_fallback/",
    )

    # Intento 1: Ticker que probablemente no existe ni en CSV
    print("\n1. Obtener datos de ticker inexistente (TICKER999)...")
    try:
        df = provider.get_historical_data(
            ticker="TICKER999",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
    except ValueError as e:
        print(f"   ✓ Excepción capturada correctamente: {str(e)[:80]}...")

    # Intento 2: Ticker existente en CSV (fallback)
    print("\n2. Obtener datos de ticker existente en CSV (UNACEMC1)...")
    try:
        df = provider.get_historical_data(
            ticker="UNACEMC1",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
        )
        print(f"   ✓ Datos cargados desde respaldo (CSV fallback)")
        print(f"   ✓ Registros obtenidos: {len(df)}")
    except ValueError as e:
        print(f"   ✗ Error: {str(e)}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "   EJEMPLOS DE USO: BVLDataProvider con Fallback a CSV".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    # Ejecutar ejemplos
    example_1_basic_usage()
    example_2_csv_provider_direct()
    example_3_validate_csv_format()
    example_4_error_handling()

    print("\n" + "=" * 80)
    print("EJEMPLOS COMPLETADOS")
    print("=" * 80 + "\n")
