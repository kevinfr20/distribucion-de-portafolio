
import logging
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional

from .base_provider import BaseDataProvider
from .local_csv_provider import LocalCSVProvider

logger = logging.getLogger(__name__)

class BVLDataProvider(BaseDataProvider):
    def __init__(self, api_base_url: str, api_timeout: int, fallback_dir: str, api_key: Optional[str] = None):
        super().__init__()
        self.api_base_url = api_base_url
        self.api_timeout = api_timeout
        self.fallback_dir = Path(fallback_dir)
        self.api_key = api_key # Store the API key
        self.local_csv_provider = LocalCSVProvider(fallback_dir=fallback_dir)

    def get_historical_data(self, ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        logger.info(f"Intentando obtener datos históricos para {ticker} desde {start_date} hasta {end_date}.")

        # Intenta obtener datos de la API
        api_data = self._fetch_from_api(ticker, start_date, end_date)

        if api_data is not None:
            # Validate API data
            if self.validate_data(api_data):
                logger.info(f"Datos obtenidos de la API para {ticker}.")
                return api_data
            else:
                logger.warning(f"Datos de la API para {ticker} fallaron la validación. Intentando con respaldo CSV local.")
        else:
            logger.warning(f"No se pudieron obtener datos de la API para {ticker}. Intentando con respaldo CSV local.")

        # Intenta obtener datos del respaldo CSV local
        local_data = self.local_csv_provider.get_historical_data(ticker, start_date, end_date)
        if local_data is not None:
            # Validate local CSV data
            if self.validate_data(local_data):
                logger.info(f"Datos obtenidos del respaldo CSV local para {ticker}.")
                return local_data
            else:
                logger.warning(f"Datos del respaldo CSV local para {ticker} fallaron la validación.")

        error_msg = (
            f"No se pudo obtener data de la API ni del respaldo CSV local para el ticker {ticker}. "
            "Verificar: 1) Conectividad a la API, 2) Validez de la API key, 3) Existencia del archivo CSV en data/bvl_fallback"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    def validate_data(self, df: pd.DataFrame) -> bool:
        # Basic validation: check if DataFrame is not empty
        if df.empty:
            logger.warning("Validation failed: DataFrame is empty.")
            return False
        # Add more validation logic here if needed (e.g., column checks, data types)
        return True

    def _fetch_from_api(self, ticker: str, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        if not self.api_key:
            logger.warning("API Key de BVL no proporcionada. Saltando la llamada a la API.")
            return None

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        url = f"{self.api_base_url}/quotes/{ticker}/historical?start_date={start_date_str}&end_date={end_date_str}"

        headers = {
            'X-API-KEY': self.api_key # Assuming 'X-API-KEY' as the header name. Adjust if different.
        }

        try:
            logger.info(f"Realizando llamada a la API de BVL para {ticker}: {url}")
            response = requests.get(url, headers=headers, timeout=self.api_timeout)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

            json_data = response.json()

            if not json_data:
                logger.warning(f"La API de BVL no retornó datos para {ticker} en el rango especificado.")
                return None

            df = pd.DataFrame(json_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            return df

        except requests.exceptions.HTTPError as e:
            logger.warning(f"Error al procesar datos de la API para {ticker}: Error HTTP de la API: {e}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Error de conexión al intentar obtener datos de la API para {ticker}: {e}")
            return None
        except requests.exceptions.Timeout:
            logger.warning(f"Tiempo de espera de la API excedido para {ticker}.")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error de solicitud de la API para {ticker}: {e}")
            return None
        except ValueError as e:
            logger.warning(f"Error al parsear JSON de la API para {ticker}: {e}")
            return None
        except KeyError as e:
            logger.warning(f"Clave faltante en la respuesta JSON de la API para {ticker}: {e}")
            return None
