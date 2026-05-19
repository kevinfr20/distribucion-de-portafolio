"""
Módulo: base_provider.py
Descripción: Define la interfaz abstracta para proveedores de datos.
Autor: Software Engineer
Fecha: 2026-05-19
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import pandas as pd


class BaseDataProvider(ABC):
    """
    Clase abstracta que define el contrato para todos los proveedores de datos.
    
    Esta clase establece la interfaz que deben cumplir todos los proveedores
    de datos históricos de cotizaciones bursátiles.
    """

    @abstractmethod
    def get_historical_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """
        Obtiene datos históricos de un ticker en un rango de fechas.

        Args:
            ticker (str): Símbolo del instrumento financiero (ej. "ALICORC1").
            start_date (datetime): Fecha de inicio del período.
            end_date (datetime): Fecha de fin del período.

        Returns:
            pd.DataFrame: DataFrame con columnas [Date, Open, High, Low, Close, Volume]
                         e índice de fecha (datetime).

        Raises:
            ValueError: Si no se pueden obtener los datos.
            ConnectionError: Si hay problemas de conectividad.
        """
        pass

    @abstractmethod
    def validate_data(self, data: pd.DataFrame, ticker: str) -> bool:
        """
        Valida que el DataFrame tenga el formato correcto.

        Args:
            data (pd.DataFrame): DataFrame a validar.
            ticker (str): Símbolo del ticker (para contexto en mensajes).

        Returns:
            bool: True si el DataFrame es válido, False en caso contrario.
        """
        pass
