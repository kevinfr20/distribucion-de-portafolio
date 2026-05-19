"""
Módulo: bvl_data_provider.py
Descripción: Proveedor de datos de la Bolsa de Valores de Lima (BVL) con fallback a CSV.
Autor: Software Engineer
Fecha: 2026-05-19
"""

import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import requests

from base_provider import BaseDataProvider
from local_csv_provider import LocalCSVProvider

# Configurar logger
logger = logging.getLogger(__name__)


class BVLDataProvider(BaseDataProvider):
    """
    Proveedor de datos para la Bolsa de Valores de Lima (BVL).
    
    Implementa un mecanismo de tolerancia a fallos (fault-tolerant) que intenta obtener
    datos de la API de BVL y, en caso de fallo, carga datos desde archivos CSV locales.
    
    Attributes:
        api_base_url (str): URL base de la API de BVL.
        api_timeout (int): Tiempo máximo de espera para la API (en segundos).
        api_key (Optional[str]): Clave de API (si es requerida).
        csv_provider (LocalCSVProvider): Instancia del proveedor de CSV para fallback.
        required_columns (list): Columnas esperadas en el resultado.
    """

    def __init__(
        self,
        api_base_url: str = "https://api.bvl.com.pe/v1",
        api_timeout: int = 30,
        api_key: Optional[str] = None,
        fallback_dir: str = "./data/bvl_fallback/",
    ):
        """
        Inicializa el proveedor de datos de BVL.

        Args:
            api_base_url (str): URL base de la API de BVL.
            api_timeout (int): Timeout para requests a la API (por defecto 30s).
            api_key (Optional[str]): Clave de API si es requerida.
            fallback_dir (str): Directorio para archivos CSV de respaldo.
        """
        self.api_base_url = api_base_url
        self.api_timeout = api_timeout
        self.api_key = api_key
        self.csv_provider = LocalCSVProvider(fallback_dir=fallback_dir)
        self.required_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]

        logger.info(
            f"BVLDataProvider inicializado: {api_base_url} "
            f"(timeout: {api_timeout}s, fallback: {fallback_dir})"
        )

    def get_historical_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """
        Obtiene datos históricos de un ticker con fallback a CSV.
        
        Proceso:
        1. Intenta obtener datos de la API de BVL.
        2. Si falla, intenta cargar desde CSV local.
        3. Si ambas fallan, lanza una excepción detallada.

        Args:
            ticker (str): Símbolo del ticker (ej. "ALICORC1").
            start_date (datetime): Fecha de inicio (inclusive).
            end_date (datetime): Fecha de fin (inclusive).

        Returns:
            pd.DataFrame: DataFrame con columnas [Date, Open, High, Low, Close, Volume].

        Raises:
            ValueError: Si no se pueden obtener datos de API ni CSV.
            ConnectionError: Si hay problemas de conectividad.

        Example:
            >>> provider = BVLDataProvider()
            >>> df = provider.get_historical_data(
            ...     ticker="ALICORC1",
            ...     start_date=datetime(2025, 1, 1),
            ...     end_date=datetime(2025, 12, 31)
            ... )
            >>> print(df.head())
        """
        ticker_upper = ticker.upper()
        
        logger.info(
            f"Obteniendo datos históricos para {ticker_upper} "
            f"desde {start_date.date()} hasta {end_date.date()}"
        )

        # Intentar obtener datos de la API
        try:
            data = self._fetch_from_api(ticker_upper, start_date, end_date)
            
            if data is not None and not data.empty:
                logger.info(f"Datos obtenidos exitosamente de la API para {ticker_upper}")
                self.validate_data(data, ticker_upper)
                return data
            
        except (ConnectionError, TimeoutError) as e:
            logger.warning(
                f"Error de conectividad al intentar obtener datos de la API para {ticker_upper}: {str(e)}"
            )
        except (ValueError, KeyError) as e:
            logger.warning(
                f"Error al procesar datos de la API para {ticker_upper}: {str(e)}"
            )
        except Exception as e:
            logger.warning(
                f"Error inesperado al obtener datos de la API para {ticker_upper}: {str(e)}"
            )

        # Fallback a CSV local
        logger.info(f"Intentando cargar datos desde respaldo CSV para {ticker_upper}...")
        
        try:
            data = self.csv_provider.load_historical_data(
                ticker=ticker_upper,
                start_date=start_date,
                end_date=end_date,
            )
            
            if data is not None and not data.empty:
                logger.info(f"Datos cargados exitosamente desde CSV para {ticker_upper}")
                self.validate_data(data, ticker_upper)
                return data
            
        except FileNotFoundError as e:
            logger.error(
                f"Archivo CSV no encontrado para {ticker_upper}: {str(e)}"
            )
        except ValueError as e:
            logger.error(
                f"Error al procesar CSV para {ticker_upper}: {str(e)}"
            )
        except Exception as e:
            logger.error(
                f"Error inesperado al cargar CSV para {ticker_upper}: {str(e)}"
            )

        # Si llegamos aquí, ambos mecanismos fallaron
        error_msg = (
            f"No se pudo obtener data de la API ni del respaldo CSV local "
            f"para el ticker {ticker_upper}. "
            f"Verificar: 1) Conectividad a la API, 2) Validez de la API key, "
            f"3) Existencia del archivo CSV en {self.csv_provider.fallback_dir}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    def _fetch_from_api(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Optional[pd.DataFrame]:
        """
        Intenta obtener datos históricos de la API de BVL.
        
        Este es un método placeholder que simula la estructura de una llamada a API real.
        Debe ser reemplazado con la implementación específica de la API de BVL.

        Args:
            ticker (str): Símbolo del ticker.
            start_date (datetime): Fecha de inicio.
            end_date (datetime): Fecha de fin.

        Returns:
            Optional[pd.DataFrame]: DataFrame si es exitosa, None si la API retorna vacío.

        Raises:
            ConnectionError: Si hay problemas de red.
            TimeoutError: Si se agota el timeout.
            ValueError: Si la respuesta es inválida.
        """
        try:
            logger.debug(f"Llamando a API de BVL para {ticker}...")

            # Construir URL (NOTA: Esta es una estructura ejemplo)
            url = f"{self.api_base_url}/quotes/{ticker}/historical"
            
            headers = {
                "User-Agent": "BVLDataProvider/1.0",
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            }

            # Realizar request
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=self.api_timeout,
            )

            # Verificar código de estado HTTP
            if response.status_code == 404:
                logger.warning(f"Ticker {ticker} no encontrado en la API (404)")
                return None
            
            if response.status_code == 401:
                raise ValueError("API key inválida o expirada (401)")
            
            if response.status_code == 500:
                raise ConnectionError("Servidor de API retornó error 500")
            
            response.raise_for_status()

            # Procesar respuesta JSON
            data = response.json()

            # Verificar que la respuesta no sea vacía
            if not data or (isinstance(data, dict) and not data.get("data")):
                logger.warning(f"API retornó respuesta vacía para {ticker}")
                return None

            # Convertir a DataFrame (estructura esperada)
            df = pd.DataFrame(data.get("data", []))

            if df.empty:
                logger.warning(f"DataFrame vacío después de procesar respuesta de API para {ticker}")
                return None

            # Estandarizar columnas (ajustar según respuesta real de API)
            df = self._standardize_api_response(df)

            return df

        except requests.exceptions.Timeout:
            raise TimeoutError(f"Timeout conectando a la API para {ticker}")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Error de conexión con la API: {str(e)}")
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"Error HTTP de la API: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Error al parsear respuesta JSON de API: {str(e)}")

    def _standardize_api_response(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estandariza la respuesta de la API al formato esperado.
        
        NOTA: Esta implementación es un placeholder. Ajustar según la estructura
        real de respuesta de la API de BVL.

        Args:
            df (pd.DataFrame): DataFrame con respuesta de API.

        Returns:
            pd.DataFrame: DataFrame estandarizado.

        Raises:
            ValueError: Si faltan columnas esperadas.
        """
        # Ejemplo de mapeo (ajustar a estructura real de API de BVL)
        expected_cols = ["date", "open", "high", "low", "close", "volume"]
        
        missing = [col for col in expected_cols if col not in df.columns]
        if missing:
            raise ValueError(
                f"Columnas faltantes en respuesta de API: {missing}. "
                f"Disponibles: {list(df.columns)}"
            )

        # Renombrar a formato estándar
        df = df.rename(columns={
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        })

        # Convertir fecha a datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.set_index("Date")

        # Convertir precios a float
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Convertir volumen a int
        df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0).astype("int64")

        # Eliminar filas con NaN
        df = df.dropna(subset=["Open", "High", "Low", "Close"])

        return df

    def validate_data(self, data: pd.DataFrame, ticker: str) -> bool:
        """
        Valida que el DataFrame tenga el formato correcto.

        Args:
            data (pd.DataFrame): DataFrame a validar.
            ticker (str): Símbolo del ticker (para contexto en mensajes).

        Returns:
            bool: True si el DataFrame es válido.

        Raises:
            ValueError: Si el DataFrame no cumple los requisitos.
        """
        if data is None or data.empty:
            raise ValueError(f"DataFrame vacío para {ticker}")

        # Verificar que tenga todas las columnas requeridas
        missing_cols = [col for col in self.required_columns if col not in data.columns]
        if missing_cols:
            raise ValueError(
                f"Columnas faltantes en datos para {ticker}: {missing_cols}"
            )

        # Verificar que el índice sea fecha
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError(f"El índice debe ser DatetimeIndex para {ticker}")

        # Verificar tipos de datos
        expected_dtypes = {
            "Open": ["float64", "float32"],
            "High": ["float64", "float32"],
            "Low": ["float64", "float32"],
            "Close": ["float64", "float32"],
            "Volume": ["int64", "int32"],
        }

        for col, allowed_types in expected_dtypes.items():
            if col in data.columns:
                actual_type = str(data[col].dtype)
                if actual_type not in allowed_types:
                    logger.warning(
                        f"Tipo de dato no óptimo para {col} en {ticker}: "
                        f"esperado {allowed_types}, obtenido {actual_type}"
                    )

        logger.debug(f"Validación exitosa para {ticker}: {len(data)} registros")
        return True
