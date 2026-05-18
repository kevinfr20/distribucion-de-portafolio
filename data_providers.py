"""
Módulo de Proveedores de Datos Abstrayendo Múltiples Fuentes

Este módulo implementa el patrón Strategy para soportar múltiples proveedores de datos
(Yahoo Finance, BVL Data, Trading Economics) de forma escalable y mantenible.

Características:
- Interfaz abstracta BaseDataProvider
- Implementaciones concretas para diferentes mercados
- Factory pattern para enrutamiento automático
- Homogenización de datos en formato estándar
- Manejo robusto de excepciones
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, List
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta
import warnings
import logging

warnings.filterwarnings('ignore')

# ==================== CONFIGURACIÓN DE LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== INTERFAZ BASE ABSTRACTA ====================
class BaseDataProvider(ABC):
    """
    Interfaz abstracta para proveedores de datos históricos.
    
    Define el contrato que todos los proveedores deben cumplir,
    asegurando homogenización en la obtención de datos.
    """
    
    STANDARD_COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    def __init__(self):
        """Inicializa el proveedor base."""
        self.provider_name = self.__class__.__name__
        self.logger = logging.getLogger(self.provider_name)
    
    @abstractmethod
    def get_historical_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Obtiene datos históricos del activo especificado.
        
        Parameters:
        -----------
        ticker : str
            Identificador del activo (ej: 'AAPL', 'ALICORC1.HE')
        start_date : str, optional
            Fecha inicio en formato YYYY-MM-DD
        end_date : str, optional
            Fecha fin en formato YYYY-MM-DD
        **kwargs : dict
            Parámetros adicionales específicos del proveedor
        
        Returns:
        --------
        pd.DataFrame
            DataFrame con columnas estándar: Date, Open, High, Low, Close, Volume
            Index: DatetimeIndex con las fechas
        
        Raises:
        -------
        ValueError
            Si los parámetros no son válidos
        ConnectionError
            Si hay problemas de conexión con la API
        """
        pass
    
    @staticmethod
    def _validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> Tuple[str, str]:
        """
        Valida y normaliza el rango de fechas.
        
        Parameters:
        -----------
        start_date : str, optional
        end_date : str, optional
        
        Returns:
        --------
        tuple : (start_date, end_date) normalizadas
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                raise ValueError("start_date no puede ser posterior a end_date")
        except ValueError as e:
            raise ValueError(f"Formato de fecha inválido. Use YYYY-MM-DD: {e}")
        
        return start_date, end_date
    
    @staticmethod
    def _standardize_dataframe(df: pd.DataFrame, expected_columns: List[str] = None) -> pd.DataFrame:
        """
        Estandariza el DataFrame al formato requerido.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame a estandarizar
        expected_columns : list, optional
            Columnas esperadas. Si no se especifica, usa STANDARD_COLUMNS
        
        Returns:
        --------
        pd.DataFrame
            DataFrame estandarizado
        """
        if df.empty:
            return df
        
        if expected_columns is None:
            expected_columns = BaseDataProvider.STANDARD_COLUMNS
        
        # Asegurar que Date está en el index como DatetimeIndex
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        elif not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Seleccionar solo columnas disponibles del estándar
        available_cols = [col for col in expected_columns if col in df.columns]
        df = df[available_cols]
        
        # Convertir a tipos numéricos
        for col in df.columns:
            if col != 'Date':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.sort_index()


# ==================== PROVEEDOR: YAHOO FINANCE ====================
class YahooFinanceProvider(BaseDataProvider):
    """
    Proveedor de datos desde Yahoo Finance.
    
    Soporta activos globales con tickers disponibles en Yahoo Finance.
    """
    
    def __init__(self):
        """Inicializa el proveedor de Yahoo Finance."""
        super().__init__()
        self.logger.info("YahooFinanceProvider inicializado")
    
    def get_historical_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Descarga datos históricos desde Yahoo Finance.
        
        Parameters:
        -----------
        ticker : str
            Ticker del activo (ej: 'AAPL', 'MSFT')
        start_date : str, optional
            Fecha inicio (YYYY-MM-DD)
        end_date : str, optional
            Fecha fin (YYYY-MM-DD)
        **kwargs : dict
            Parámetros adicionales (no utilizados aquí)
        
        Returns:
        --------
        pd.DataFrame
            DataFrame estandarizado con datos históricos
        """
        try:
            start_date, end_date = self._validate_date_range(start_date, end_date)
            
            self.logger.info(f"📥 Descargando {ticker} desde Yahoo Finance ({start_date} a {end_date})")
            
            # Descargar datos de Yahoo Finance
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                self.logger.warning(f"⚠️ No hay datos disponibles para {ticker} en el rango especificado")
                return pd.DataFrame()
            
            # Si es un único ticker, yfinance devuelve Series, convertir a DataFrame
            if isinstance(data, pd.Series):
                data = data.to_frame()
            
            # Manejar MultiIndex si hay múltiples tickers
            if isinstance(data.columns, pd.MultiIndex):
                # Seleccionar solo el primer ticker si es MultiIndex
                data = data.iloc[:, :6] if len(data.columns) >= 6 else data
            
            # Estandarizar columnas
            column_mapping = {
                'Adj Close': 'Close',
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Volume': 'Volume'
            }
            
            data.rename(columns=column_mapping, inplace=True)
            data = self._standardize_dataframe(data)
            
            self.logger.info(f"✅ {len(data)} registros descargados para {ticker}")
            return data
            
        except Exception as e:
            self.logger.error(f"❌ Error descargando {ticker} desde Yahoo Finance: {str(e)}")
            return pd.DataFrame()


# ==================== PROVEEDOR: BVL DATA ====================
class BVLDataProvider(BaseDataProvider):
    """
    Proveedor de datos desde la API de la Bolsa de Valores de Lima (BVL).
    
    Soporta activos peruanos sin ADR en mercados internacionales.
    Requiere API Key para autenticación.
    """
    
    # Endpoints de ejemplo (ajustar según documentación real de BVL)
    BASE_URL = "https://api.bvl.com.pe/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el proveedor de BVL.
        
        Parameters:
        -----------
        api_key : str, optional
            Clave API para autenticación en BVL
        """
        super().__init__()
        self.api_key = api_key
        self.session = requests.Session()
        self.logger.info("BVLDataProvider inicializado")
    
    def _get_headers(self) -> Dict[str, str]:
        """Genera headers para las peticiones a BVL."""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PortfolioOptimizer/1.0'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        timeout: int = 10
    ) -> Optional[Dict]:
        """
        Realiza una petición HTTP a la API de BVL.
        
        Parameters:
        -----------
        endpoint : str
            Endpoint relativo (ej: '/quotes/ALICORC1')
        params : dict, optional
            Parámetros de la petición
        timeout : int
            Timeout en segundos
        
        Returns:
        --------
        dict or None
            Respuesta JSON o None si hay error
        """
        try:
            url = f"{self.BASE_URL}{endpoint}"
            headers = self._get_headers()
            
            self.logger.debug(f"Realizando petición a: {url}")
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            self.logger.error(f"❌ Timeout al conectar a BVL (endpoint: {endpoint})")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"❌ Error de conexión a BVL (endpoint: {endpoint})")
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"❌ Error HTTP en BVL: {response.status_code} - {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error inesperado en petición a BVL: {str(e)}")
            return None
    
    def get_historical_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Obtiene datos históricos desde la API de BVL.
        
        Parameters:
        -----------
        ticker : str
            Ticker BVL (ej: 'ALICORC1.HE', 'VOLCABC1.HE')
        start_date : str, optional
            Fecha inicio (YYYY-MM-DD)
        end_date : str, optional
            Fecha fin (YYYY-MM-DD)
        **kwargs : dict
            Parámetros adicionales (ej: frequency='daily')
        
        Returns:
        --------
        pd.DataFrame
            DataFrame estandarizado con datos históricos
        """
        try:
            start_date, end_date = self._validate_date_range(start_date, end_date)
            
            self.logger.info(f"📥 Descargando {ticker} desde BVL API ({start_date} a {end_date})")
            
            # Parámetros para la petición
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'frequency': kwargs.get('frequency', 'daily')
            }
            
            # Endpoint de históricos de BVL (ajustar según documentación real)
            endpoint = f'/quotes/{ticker}/history'
            data_json = self._make_request(endpoint, params)
            
            if not data_json or 'data' not in data_json:
                self.logger.warning(f"⚠️ No hay datos disponibles para {ticker} en BVL")
                return pd.DataFrame()
            
            # Procesar respuesta JSON a DataFrame
            df = pd.DataFrame(data_json['data'])
            
            # Mapear columnas según respuesta de BVL
            column_mapping = {
                'fecha': 'Date',
                'apertura': 'Open',
                'maximo': 'High',
                'minimo': 'Low',
                'cierre': 'Close',
                'volumen': 'Volume',
                'date': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            df = self._standardize_dataframe(df)
            
            self.logger.info(f"✅ {len(df)} registros descargados para {ticker} desde BVL")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error descargando {ticker} desde BVL: {str(e)}")
            return pd.DataFrame()


# ==================== PROVEEDOR: TRADING ECONOMICS ====================
class TradingEconomicsProvider(BaseDataProvider):
    """
    Proveedor de datos desde Trading Economics.
    
    Especializado en índices macroeconómicos y bursátiles de Perú.
    """
    
    BASE_URL = "https://api.tradingeconomics.com"
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Inicializa el proveedor de Trading Economics.
        
        Parameters:
        -----------
        api_token : str, optional
            Token API para Trading Economics
        """
        super().__init__()
        self.api_token = api_token
        self.session = requests.Session()
        self.logger.info("TradingEconomicsProvider inicializado")
    
    def _get_params(self) -> Dict[str, str]:
        """Genera parámetros estándar para peticiones."""
        params = {'format': 'json'}
        if self.api_token:
            params['c'] = self.api_token
        return params
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        timeout: int = 10
    ) -> Optional[List[Dict]]:
        """
        Realiza una petición HTTP a Trading Economics.
        
        Parameters:
        -----------
        endpoint : str
            Endpoint (ej: '/markets/index/SPBLPGPT')
        params : dict, optional
            Parámetros adicionales
        timeout : int
            Timeout en segundos
        
        Returns:
        --------
        list or None
            Lista de datos o None si hay error
        """
        try:
            url = f"{self.BASE_URL}{endpoint}"
            request_params = self._get_params()
            if params:
                request_params.update(params)
            
            self.logger.debug(f"Realizando petición a: {url}")
            response = self.session.get(url, params=request_params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            return data if isinstance(data, list) else [data]
            
        except requests.exceptions.Timeout:
            self.logger.error(f"❌ Timeout al conectar a Trading Economics")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"❌ Error de conexión a Trading Economics")
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"❌ Error HTTP en Trading Economics: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error inesperado en Trading Economics: {str(e)}")
            return None
    
    def get_historical_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Obtiene datos históricos de índices desde Trading Economics.
        
        Parameters:
        -----------
        ticker : str
            Identificador del índice (ej: 'SPBLPGPT' para S&P BVL General)
        start_date : str, optional
            Fecha inicio (YYYY-MM-DD)
        end_date : str, optional
            Fecha fin (YYYY-MM-DD)
        **kwargs : dict
            Parámetros adicionales
        
        Returns:
        --------
        pd.DataFrame
            DataFrame estandarizado con datos históricos
        """
        try:
            start_date, end_date = self._validate_date_range(start_date, end_date)
            
            self.logger.info(f"📥 Descargando {ticker} desde Trading Economics ({start_date} a {end_date})")
            
            # Endpoint para datos históricos de índices
            endpoint = f'/markets/index/{ticker}/historical'
            
            data_list = self._make_request(
                endpoint,
                params={'d1date': start_date, 'd2date': end_date}
            )
            
            if not data_list:
                self.logger.warning(f"⚠️ No hay datos disponibles para {ticker} en Trading Economics")
                return pd.DataFrame()
            
            # Procesar respuesta
            df = pd.DataFrame(data_list)
            
            # Mapear columnas según respuesta de Trading Economics
            column_mapping = {
                'Date': 'Date',
                'Value': 'Close',
                'LastUpdate': 'Date'
            }
            
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            elif 'LastUpdate' in df.columns:
                df['Date'] = pd.to_datetime(df['LastUpdate'])
                
            # Para índices, solo tenemos valor de cierre
            if 'Value' in df.columns:
                df.rename(columns={'Value': 'Close'}, inplace=True)
            elif 'Close' not in df.columns and len(df.columns) > 0:
                # Usar la primera columna numérica como Close
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    df.rename(columns={numeric_cols[0]: 'Close'}, inplace=True)
            
            # Crear OHLCV estándar (para índices, duplicar el valor)
            if 'Close' in df.columns:
                df['Open'] = df['Close']
                df['High'] = df['Close']
                df['Low'] = df['Close']
                df['Volume'] = 0  # No disponible para índices
            
            df = self._standardize_dataframe(df)
            
            self.logger.info(f"✅ {len(df)} registros descargados para {ticker} desde Trading Economics")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error descargando {ticker} desde Trading Economics: {str(e)}")
            return pd.DataFrame()


# ==================== FACTORÍA DE PROVEEDORES ====================
class DataProviderFactory:
    """
    Factory que enruta automáticamente a la fuente de datos correcta según el ticker.
    
    Implementa lógica de identificación de mercado basada en patrones de tickers.
    """
    
    # Patrones de tickers para identificar mercados
    BVL_PATTERNS = ['.HE', '.HN', '.HB', '.HA']  # Sufijos típicos de BVL
    TRADING_ECONOMICS_TICKERS = ['SPBLPGPT', 'SPBLPGEN']  # Índices de Perú
    
    def __init__(
        self,
        bvl_api_key: Optional[str] = None,
        trading_economics_token: Optional[str] = None
    ):
        """
        Inicializa la factoría con credenciales opcionales.
        
        Parameters:
        -----------
        bvl_api_key : str, optional
            Clave API para BVL
        trading_economics_token : str, optional
            Token para Trading Economics
        """
        self.bvl_api_key = bvl_api_key
        self.trading_economics_token = trading_economics_token
        
        # Instanciar proveedores
        self.yahoo_provider = YahooFinanceProvider()
        self.bvl_provider = BVLDataProvider(api_key=bvl_api_key)
        self.trading_economics_provider = TradingEconomicsProvider(api_token=trading_economics_token)
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def identify_market(self, ticker: str) -> str:
        """
        Identifica el mercado de origen del ticker.
        
        Parameters:
        -----------
        ticker : str
            Ticker a identificar
        
        Returns:
        --------
        str
            Mercado identificado: 'bvl', 'trading_economics' o 'yahoo'
        """
        ticker_upper = ticker.upper()
        
        # Verificar si es un índice de Trading Economics
        if ticker_upper in self.TRADING_ECONOMICS_TICKERS:
            self.logger.debug(f"Mercado identificado para {ticker}: Trading Economics")
            return 'trading_economics'
        
        # Verificar si es un ticker de BVL
        for pattern in self.BVL_PATTERNS:
            if ticker_upper.endswith(pattern):
                self.logger.debug(f"Mercado identificado para {ticker}: BVL")
                return 'bvl'
        
        # Búsqueda heurística adicional para tickers peruanos
        if any(keyword in ticker_upper for keyword in ['PERU', 'BVL', 'VOLC', 'ALICORP', 'FERREYC']):
            self.logger.debug(f"Mercado identificado para {ticker}: BVL (heurística)")
            return 'bvl'
        
        # Por defecto, usar Yahoo Finance
        self.logger.debug(f"Mercado identificado para {ticker}: Yahoo Finance (default)")
        return 'yahoo'
    
    def get_provider(self, ticker: str) -> BaseDataProvider:
        """
        Obtiene el proveedor apropiado para un ticker.
        
        Parameters:
        -----------
        ticker : str
            Ticker para el cual obtener el proveedor
        
        Returns:
        --------
        BaseDataProvider
            Instancia del proveedor correcto
        """
        market = self.identify_market(ticker)
        
        if market == 'bvl':
            return self.bvl_provider
        elif market == 'trading_economics':
            return self.trading_economics_provider
        else:
            return self.yahoo_provider
    
    def fetch_data(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Descarga datos históricos para múltiples tickers, enrutando a la fuente correcta.
        
        Parameters:
        -----------
        tickers : list
            Lista de tickers a descargar
        start_date : str, optional
            Fecha inicio (YYYY-MM-DD)
        end_date : str, optional
            Fecha fin (YYYY-MM-DD)
        **kwargs : dict
            Parámetros adicionales para proveedores específicos
        
        Returns:
        --------
        pd.DataFrame
            DataFrame consolidado con datos de todos los tickers
        """
        if not tickers:
            self.logger.warning("⚠️ Lista de tickers vacía")
            return pd.DataFrame()
        
        all_data = {}
        
        for ticker in tickers:
            provider = self.get_provider(ticker)
            data = provider.get_historical_data(ticker, start_date, end_date, **kwargs)
            
            if not data.empty:
                # Usar el nombre del ticker como columna si hay múltiples tickers
                if len(tickers) > 1:
                    # Usar solo la columna Close para múltiples tickers
                    all_data[ticker] = data['Close']
                else:
                    # Si es un solo ticker, devolver el DataFrame completo
                    return data
        
        # Consolidar datos de múltiples tickers
        if all_data:
            consolidated_df = pd.DataFrame(all_data)
            self.logger.info(f"✅ Datos consolidados para {len(all_data)} activos")
            return consolidated_df
        else:
            self.logger.warning("⚠️ No se pudieron obtener datos para ninguno de los tickers")
            return pd.DataFrame()


# ==================== FUNCIONES DE UTILIDAD ====================
def create_data_provider_factory(
    bvl_api_key: Optional[str] = None,
    trading_economics_token: Optional[str] = None
) -> DataProviderFactory:
    """
    Crea una instancia de la factoría de proveedores.
    
    Parameters:
    -----------
    bvl_api_key : str, optional
        Clave API para BVL
    trading_economics_token : str, optional
        Token para Trading Economics
    
    Returns:
    --------
    DataProviderFactory
        Instancia de la factoría
    """
    return DataProviderFactory(bvl_api_key, trading_economics_token)


# ==================== EJEMPLO DE USO ====================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 DEMOSTRACIÓN: SISTEMA DE PROVEEDORES DE DATOS MÚLTIPLES")
    print("="*80 + "\n")
    
    # Crear factoría (sin credenciales reales para este ejemplo)
    factory = DataProviderFactory()
    
    # Ejemplos de tickers de diferentes mercados
    test_cases = [
        ('AAPL', 'Yahoo Finance - Tech Stock'),
        ('ALICORC1.HE', 'BVL - Alicorp'),
        ('VOLCABC1.HE', 'BVL - Volcan'),
        ('SPBLPGPT', 'Trading Economics - S&P BVL General'),
    ]
    
    print("📊 IDENTIFICACIÓN AUTOMÁTICA DE MERCADOS:\n")
    for ticker, description in test_cases:
        market = factory.identify_market(ticker)
        provider = factory.get_provider(ticker)
        print(f"  ✓ {ticker:20} → {market:20} ({provider.provider_name})")
        print(f"    Descripción: {description}\n")
    
    # Ejemplo de descarga (solo AAPL funcionará sin credenciales reales)
    print("\n📥 DESCARGANDO DATOS (AAPL - ejemplo funcional):\n")
    try:
        data = factory.fetch_data(['AAPL'], start_date='2024-01-01', end_date='2024-03-31')
        if not data.empty:
            print(f"✅ Datos descargados exitosamente")
            print(f"   Registros: {len(data)}")
            print(f"   Columnas: {list(data.columns)}")
            print(f"\n📋 Primeras filas:\n{data.head()}")
        else:
            print("⚠️ No se pudieron descargar los datos")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("="*80 + "\n")
