"""
Módulo: local_csv_provider.py
Descripción: Proveedor de datos que carga información desde archivos CSV locales.
Autor: Software Engineer
Fecha: 2026-05-19
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Configurar logger
logger = logging.getLogger(__name__)


class LocalCSVProvider:
    """
    Proveedor de datos que carga información histórica desde archivos CSV locales.
    
    Se utiliza como mecanismo de contingencia (fallback) cuando la API externa falla.
    
    Attributes:
        fallback_dir (Path): Ruta del directorio que contiene los archivos CSV.
        encoding (str): Codificación de los archivos CSV (por defecto: 'utf-8').
        delimiter (str): Delimitador usado en los archivos CSV (por defecto: ';').
    """

    def __init__(
        self,
        fallback_dir: str = "/content/drive/MyDrive/BVL_Data",
        encoding: str = "utf-8",
        delimiter: str = ";",
    ):
        """
        Inicializa el proveedor de CSV local.

        Args:
            fallback_dir (str): Ruta del directorio con los CSVs. Por defecto "./data/bvl_fallback/".
            encoding (str): Codificación de los archivos. Por defecto "utf-8".
            delimiter (str): Delimitador del CSV. Por defecto ";".
        """
        self.fallback_dir = Path(BVL_Data)
        self.encoding = encoding
        self.delimiter = delimiter

        # Crear directorio si no existe
        self.fallback_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio de respaldo CSV inicializado: {self.fallback_dir.absolute()}")

    def get_csv_path(self, ticker: str) -> Path:
        """
        Construye la ruta del archivo CSV para un ticker.

        Args:
            ticker (str): Símbolo del ticker (ej. "ALICORC1").

        Returns:
            Path: Ruta del archivo CSV.

        Example:
            >>> provider = LocalCSVProvider()
            >>> path = provider.get_csv_path("ALICORC1")
            >>> print(path)
            data/bvl_fallback/ALICORC1.csv
        """
        ticker_upper = ticker.upper()
        csv_filename = f"{ticker_upper}.csv"
        return self.fallback_dir / csv_filename

    def file_exists(self, ticker: str) -> bool:
        """
        Verifica si existe el archivo CSV para un ticker.

        Args:
            ticker (str): Símbolo del ticker.

        Returns:
            bool: True si el archivo existe, False en caso contrario.
        """
        csv_path = self.get_csv_path(ticker)
        exists = csv_path.exists() and csv_path.is_file()
        
        if exists:
            logger.debug(f"Archivo CSV encontrado para {ticker}: {csv_path.absolute()}")
        else:
            logger.debug(f"Archivo CSV NO encontrado para {ticker}: {csv_path.absolute()}")
        
        return exists

    def load_historical_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """
        Carga datos históricos desde un archivo CSV local.

        Operaciones:
        1. Verifica que el archivo exista.
        2. Lee el CSV con Pandas.
        3. Parsea la columna 'Fecha de cotización' como datetime.
        4. Filtra por el rango de fechas solicitado.
        5. Estandariza los nombres de columnas y tipos de datos.

        Args:
            ticker (str): Símbolo del ticker.
            start_date (datetime): Fecha de inicio (inclusive).
            end_date (datetime): Fecha de fin (inclusive).

        Returns:
            pd.DataFrame: DataFrame con columnas [Date, Open, High, Low, Close, Volume]
                         indexado por fecha.

        Raises:
            FileNotFoundError: Si el archivo CSV no existe.
            ValueError: Si el CSV está corrupto o no tiene el formato esperado.
            pd.errors.ParserError: Si hay errores al parsear el CSV.

        Example:
            >>> provider = LocalCSVProvider()
            >>> df = provider.load_historical_data(
            ...     ticker="ALICORC1",
            ...     start_date=datetime(2025, 1, 1),
            ...     end_date=datetime(2025, 12, 31)
            ... )
            >>> print(df.head())
        """
        csv_path = self.get_csv_path(ticker)

        # Verificar que el archivo exista
        if not csv_path.exists():
            raise FileNotFoundError(
                f"Archivo CSV no encontrado para {ticker}: {csv_path.absolute()}"
            )

        try:
            logger.info(f"Cargando datos históricos desde CSV: {csv_path.absolute()}")

            # Leer el CSV con el delimitador y encoding especificados
            df = pd.read_csv(
                csv_path,
                delimiter=self.delimiter,
                encoding=self.encoding,
                dtype_backend="numpy_nullable",
            )

            logger.debug(f"CSV leído exitosamente. Filas: {len(df)}, Columnas: {list(df.columns)}")

            # Verificar que tenga la columna de fecha
            if "Fecha de cotización" not in df.columns:
                raise ValueError(
                    f"La columna 'Fecha de cotización' no existe en {csv_path.name}. "
                    f"Columnas disponibles: {list(df.columns)}"
                )

            # Parsear la columna de fecha
            df["Fecha de cotización"] = pd.to_datetime(
                df["Fecha de cotización"],
                format="%d/%m/%Y",
                errors="coerce",
            )

            # Remover filas con fechas inválidas
            rows_before = len(df)
            df = df.dropna(subset=["Fecha de cotización"])
            rows_dropped = rows_before - len(df)

            if rows_dropped > 0:
                logger.warning(
                    f"Se descartaron {rows_dropped} filas con fechas inválidas de {csv_path.name}"
                )

            # Filtrar por rango de fechas
            df = df[
                (df["Fecha de cotización"] >= start_date)
                & (df["Fecha de cotización"] <= end_date)
            ].copy()

            if df.empty:
                logger.warning(
                    f"No hay datos en el rango [{start_date.date()}, {end_date.date()}] "
                    f"para el ticker {ticker}"
                )
                return self._create_empty_dataframe()

            # Estandarizar nombres de columnas
            df = self._standardize_columns(df)

            # Validar y corregir tipos de datos
            df = self._standardize_dtypes(df)

            logger.info(
                f"Datos cargados exitosamente desde CSV para {ticker}. "
                f"Filas: {len(df)}, Período: {df.index.min().date()} a {df.index.max().date()}"
            )

            return df

        except pd.errors.ParserError as e:
            raise ValueError(
                f"Error al parsear el archivo CSV {csv_path.name}: {str(e)}"
            ) from e
        except KeyError as e:
            raise ValueError(
                f"Columna requerida no encontrada en {csv_path.name}: {str(e)}"
            ) from e
        except Exception as e:
            raise ValueError(
                f"Error inesperado al cargar CSV para {ticker}: {str(e)}"
            ) from e

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estandariza los nombres de columnas del CSV al formato esperado.

        Mapeo de columnas:
        - "Fecha de cotización" -> "Date" (índice)
        - "Apertura" -> "Open"
        - "Máximo" -> "High"
        - "Mínimo" -> "Low"
        - "Cierre" -> "Close"
        - "Cantidad negociada" -> "Volume"

        Args:
            df (pd.DataFrame): DataFrame con columnas originales.

        Returns:
            pd.DataFrame: DataFrame con columnas estandarizadas e indexado por fecha.

        Raises:
            ValueError: Si faltan columnas críticas.
        """
        # Mapeo de columnas del CSV de BVL a formato estándar
        column_mapping = {
            "Fecha de cotización": "Date",
            "Apertura": "Open",
            "Máximo": "High",
            "Mínimo": "Low",
            "Cierre": "Close",
            "Cantidad negociada": "Volume",
        }

        # Verificar que todas las columnas necesarias existan
        missing_cols = [
            orig for orig in column_mapping.keys() if orig not in df.columns
        ]
        if missing_cols:
            raise ValueError(
                f"Columnas faltantes en el CSV: {missing_cols}. "
                f"Columnas disponibles: {list(df.columns)}"
            )

        # Renombrar columnas
        df = df.rename(columns=column_mapping)

        # Seleccionar solo las columnas estandarizadas
        standard_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
        df = df[standard_cols].copy()

        # Establecer 'Date' como índice
        df.set_index("Date", inplace=True)
        df.index.name = None

        return df

    def _standardize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estandariza los tipos de datos del DataFrame.

        Conversiones:
        - Open, High, Low, Close -> float64
        - Volume -> int64
        - Index (Date) -> datetime64[ns]

        Args:
            df (pd.DataFrame): DataFrame con columnas ya renombradas.

        Returns:
            pd.DataFrame: DataFrame con tipos de datos estandarizados.

        Raises:
            ValueError: Si hay valores que no pueden convertirse.
        """
        price_columns = ["Open", "High", "Low", "Close"]
        volume_column = "Volume"

        try:
            # Convertir columnas de precio a float
            for col in price_columns:
                if col in df.columns:
                    # Reemplazar comas por puntos (formato local de BVL)
                    df[col] = df[col].astype(str).str.replace(",", ".")
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Convertir volumen a int
            if volume_column in df.columns:
                df[volume_column] = pd.to_numeric(df[volume_column], errors="coerce").fillna(0).astype("int64")

            # Remover filas con valores NaN en precios
            df = df.dropna(subset=price_columns)

            logger.debug(f"Tipos de datos estandarizados: {df.dtypes.to_dict()}")

            return df

        except Exception as e:
            raise ValueError(f"Error al estandarizar tipos de datos: {str(e)}") from e

    def _create_empty_dataframe(self) -> pd.DataFrame:
        """
        Crea un DataFrame vacío con la estructura esperada.

        Returns:
            pd.DataFrame: DataFrame vacío con columnas [Open, High, Low, Close, Volume]
                         e índice de fecha.
        """
        df = pd.DataFrame(
            columns=["Open", "High", "Low", "Close", "Volume"]
        )
        df.index = pd.DatetimeIndex([], name="Date")
        return df

    def save_historical_data(
        self,
        ticker: str,
        data: pd.DataFrame,
    ) -> None:
        """
        Guarda datos históricos en un archivo CSV local.

        Utilidad para guardar datos de respaldo cuando se obtienen de la API.

        Args:
            ticker (str): Símbolo del ticker.
            data (pd.DataFrame): DataFrame con los datos a guardar.

        Raises:
            IOError: Si hay problemas al escribir el archivo.
        """
        csv_path = self.get_csv_path(ticker)

        try:
            logger.info(f"Guardando datos en CSV para {ticker}: {csv_path.absolute()}")
            data.to_csv(csv_path, encoding=self.encoding, delimiter=self.delimiter)
            logger.info(f"Datos guardados exitosamente en {csv_path.absolute()}")
        except IOError as e:
            logger.error(f"Error al guardar CSV para {ticker}: {str(e)}")
            raise
