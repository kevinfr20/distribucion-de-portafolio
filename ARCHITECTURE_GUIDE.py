"""
GUÍA DE ARQUITECTURA: SISTEMA MULTI-PROVEEDOR DE DATOS
======================================================

Documento de referencia para entender la refactorización del módulo de obtención
de datos del Sistema Integrado de Gestión y Optimización de Portafolios.
"""

# ==================== 1. PROBLEMA Y SOLUCIÓN ====================

"""
PROBLEMA ORIGINAL:
==================

El sistema original (unified_portfolio_colab.py) tenía una clase DataFetcher
con lógica acoplada que descargaba datos exclusivamente desde Yahoo Finance:

    class DataFetcher:
        @staticmethod
        def fetch_data(tickers, start_date=None, end_date=None):
            data = yf.download(tickers, ...)  # <-- Solo Yahoo Finance
            return data
            
LIMITACIONES:
- No soportaba activos peruanos sin ADR (ALICORC1.HE, VOLCABC1.HE, etc.)
- No había forma de agregar nuevas fuentes sin modificar código existente
- Lógica monolítica difícil de testear y mantener
- No escalable para múltiples mercados


SOLUCIÓN IMPLEMENTADA:
======================

Se refactoriza usando el Patrón Strategy + Factory Pattern:

┌─────────────────────────────────────────────────────────────────┐
│                    DataProviderFactory                          │
│  Identifica mercado → Enruta a proveedor correcto              │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─→ Yahoo Finance       (Activos globales: AAPL, MSFT)
         ├─→ BVL Data            (Peruanos: ALICORC1.HE, VOLCABC1.HE)
         └─→ Trading Economics   (Índices: SPBLPGPT)

Cada proveedor implementa la interfaz BaseDataProvider.
"""


# ==================== 2. COMPONENTES PRINCIPALES ====================

"""
A. INTERFAZ ABSTRACTA: BaseDataProvider
========================================

Ubicación: data_providers.py

Define el contrato que todo proveedor debe cumplir:

    class BaseDataProvider(ABC):
        @abstractmethod
        def get_historical_data(
            self,
            ticker: str,
            start_date: Optional[str],
            end_date: Optional[str],
            **kwargs
        ) -> pd.DataFrame:
            '''Devuelve DataFrame con columnas estándar: Date, Open, High, Low, Close, Volume'''
            pass

VENTAJAS:
- Contrato claro y documentado
- Fácil de testear (duck typing)
- Escalable (agregar nuevos proveedores sin cambiar código existente)
- Homogenización de datos


B. IMPLEMENTACIONES CONCRETAS
=============================

1. YahooFinanceProvider
   ─────────────────────
   - Soporta: Activos globales (AAPL, MSFT, GOOGL, etc.)
   - Método: yfinance.download()
   - Autenticación: Ninguna (API pública)
   - Dividendos: ✓ Soportados
   
2. BVLDataProvider
   ────────────────
   - Soporta: Activos peruanos sin ADR (ALICORC1.HE, VOLCABC1.HE, etc.)
   - Método: REST API de BVL Data
   - Autenticación: API Key requerida
   - Endpoints: /quotes/{ticker}/history
   - Manejo de errores: Robusto (timeout, conexión, HTTP)
   
3. TradingEconomicsProvider
   ─────────────────────────
   - Soporta: Índices macroeconómicos (SPBLPGPT)
   - Método: REST API de Trading Economics
   - Autenticación: Token API (opcional para datos públicos)
   - Especialidad: Índices bursátiles nacionales


C. FACTORÍA: DataProviderFactory
=================================

Ubicación: data_providers.py

Responsabilidades:
1. Identificar el mercado del ticker
2. Enrutar al proveedor correcto
3. Descargar datos de múltiples fuentes
4. Consolidar datos en un solo DataFrame

Identificación de Mercado:
    
    # Patrones de BVL
    BVL_PATTERNS = ['.HE', '.HN', '.HB', '.HA']
    
    # Índices de Trading Economics
    TRADING_ECONOMICS_TICKERS = ['SPBLPGPT', 'SPBLPGEN']
    
    # Por defecto: Yahoo Finance

Ejemplo:
    
    factory = DataProviderFactory(bvl_api_key='clave', te_token='token')
    
    # Identifica automáticamente
    market = factory.identify_market('ALICORC1.HE')  # → 'bvl'
    
    # Enruta al proveedor correcto
    provider = factory.get_provider('ALICORC1.HE')   # → BVLDataProvider()
    
    # Descarga consolidada
    data = factory.fetch_data(['AAPL', 'ALICORC1.HE', 'SPBLPGPT'])


D. WRAPPER: DataFetcher (data_fetcher_integration.py)
=====================================================

Proporciona compatibilidad hacia atrás con código existente:

    # Interfaz original (estática)
    prices = DataFetcher.fetch_data(['AAPL', 'MSFT'], ...)
    
    # Nueva interfaz (dinámica con credenciales)
    fetcher = DataFetcher(bvl_api_key='clave')
    prices = fetcher.fetch_data_dynamic(['ALICORC1.HE'], ...)
"""


# ==================== 3. FLUJO DE DATOS ====================

"""
FLUJO TÍPICO DE USO
===================

1. Usuario solicita datos para múltiples tickers
   ↓
2. DataFetcher.fetch_data(['AAPL', 'ALICORC1.HE', 'SPBLPGPT'])
   ↓
3. DataFetcher crea DataProviderFactory
   ↓
4. Factory agrupa tickers por mercado:
   - Yahoo: ['AAPL']
   - BVL: ['ALICORC1.HE']
   - TE: ['SPBLPGPT']
   ↓
5. Para cada grupo:
   - Obtiene proveedor: factory.get_provider(ticker)
   - Descarga datos: provider.get_historical_data(ticker, ...)
   ↓
6. Estandariza formato:
   - Todas las respuestas → DataFrame con columnas estándar
   ↓
7. Consolida en un único DataFrame
   ↓
8. Retorna a UnifiedPortfolioManager
   ↓
9. Portfolio Manager optimiza sin cambios en su código


ESTANDARIZACIÓN DE DATOS
========================

Todas las respuestas se normalizan a este formato:

    DataFrame con:
    ┌──────────────┬────────┬────────┬────────┬────────┬─────────┐
    │    Date      │ Open   │ High   │ Low    │ Close  │ Volume  │
    ├──────────────┼────────┼────────┼────────┼────────┼─────────┤
    │ 2024-01-01   │ 150.5  │ 152.1  │ 150.2  │ 151.8  │ 5000000 │
    │ 2024-01-02   │ 151.8  │ 153.2  │ 151.5  │ 152.9  │ 4500000 │
    │ ...          │  ...   │  ...   │  ...   │  ...   │   ...   │
    └──────────────┴────────┴────────┴────────┴────────┴─────────┘
    
    Index: DatetimeIndex
    Tipos: float64 para OHLCV

BENEFICIOS:
- UnifiedPortfolioManager no necesita cambios
- Fácil de agregar nuevas columnas
- Compatible con análisis técnico
"""


# ==================== 4. DIAGRAMA DE CLASES ====================

"""
ESTRUCTURA UML SIMPLIFICADA
===========================

┌──────────────────────────────────────────────────────────────────┐
│                    <<abstract>>                                  │
│                   BaseDataProvider                               │
├──────────────────────────────────────────────────────────────────┤
│ # STANDARD_COLUMNS = ['Date', 'Open', 'High', 'Low', ...]       │
├──────────────────────────────────────────────────────────────────┤
│ + get_historical_data(ticker, start_date, end_date) → DataFrame │
│ + _validate_date_range(start, end) → Tuple                      │
│ + _standardize_dataframe(df) → DataFrame                         │
└──────────────────────────────────────────────────────────────────┘
         ▲                ▲                    ▲
         │                │                    │
         │                │                    │
    ┌────┴────┐    ┌──────┴──────┐    ┌───────┴────────┐
    │  Yahoo  │    │    BVL      │    │   Trading      │
    │ Finance │    │    Data     │    │  Economics     │
    │Provider │    │  Provider   │    │   Provider     │
    └─────────┘    └─────────────┘    └────────────────┘
         ▲                ▲                    ▲
         └────────┬───────┴────────┬──────────┘
                  │                │
         ┌────────┴────────────────┴────────┐
         │    DataProviderFactory           │
         ├──────────────────────────────────┤
         │ - yahoo_provider                 │
         │ - bvl_provider                   │
         │ - trading_economics_provider     │
         ├──────────────────────────────────┤
         │ + identify_market(ticker) → str  │
         │ + get_provider(ticker) → Base    │
         │ + fetch_data(tickers, ...) → DF  │
         └──────────────────────────────────┘
                   ▲
                   │
         ┌─────────┴──────────┐
         │    DataFetcher     │
         │   (Wrapper)        │
         ├────────────────────┤
         │ - factory: Factory │
         ├────────────────────┤
         │ + fetch_data(...) │
         │ + fetch_dynamic(..│
         │ + get_market_info│
         └────────────────────┘
                   ▲
                   │
         ┌─────────┴──────────────────┐
         │ UnifiedPortfolioManager    │
         │ (SIN CAMBIOS)              │
         └────────────────────────────┘
"""


# ==================== 5. GUÍA DE USO ====================

"""
CASO 1: Portafolio Global (Yahoo Finance)
==========================================

from data_fetcher_integration import DataFetcher
from unified_portfolio_colab import UnifiedPortfolioManager

# 1. Descargar datos
fetcher = DataFetcher()
prices = fetcher.fetch_data_dynamic(
    tickers=['AAPL', 'MSFT', 'GOOGL'],
    start_date='2023-01-01',
    end_date='2024-12-31'
)

# 2. Crear portafolio (sin cambios)
portfolio = UnifiedPortfolioManager(prices)

# 3. Optimizar (sin cambios)
optimal = portfolio.optimize_portfolio('sharpe')


CASO 2: Portafolio Peruano (BVL)
================================

# Necesita credenciales de BVL
fetcher = DataFetcher(bvl_api_key='tu_api_key_aqui')

prices = fetcher.fetch_data_dynamic(
    tickers=['ALICORC1.HE', 'VOLCABC1.HE', 'FERREYCORP1.HE'],
    start_date='2023-01-01',
    end_date='2024-12-31'
)

portfolio = UnifiedPortfolioManager(prices)
optimal = portfolio.optimize_portfolio('sharpe')


CASO 3: Portafolio Mixto (Global + Perú)
=========================================

# Combina múltiples mercados automáticamente
fetcher = DataFetcher(bvl_api_key='tu_api_key_aqui')

prices = fetcher.fetch_data_dynamic(
    tickers=[
        'AAPL',           # Yahoo Finance
        'MSFT',           # Yahoo Finance
        'ALICORC1.HE',    # BVL
        'VOLCABC1.HE',    # BVL
        'SPBLPGPT'        # Trading Economics (índice)
    ],
    start_date='2023-01-01',
    end_date='2024-12-31'
)

# Define pesos
weights = [0.25, 0.25, 0.20, 0.20, 0.10]

portfolio = UnifiedPortfolioManager(prices, weights=weights)

# Obtener resumen
summary = portfolio.get_portfolio_summary()
print(f"Retorno esperado: {summary['expected_return']*100:.2f}%")
print(f"Volatilidad: {summary['volatility']*100:.2f}%")
print(f"Sharpe Ratio: {summary['sharpe_ratio']:.4f}")

# Optimizar
optimal = portfolio.optimize_portfolio('sharpe')
print(f"Pesos óptimos: {optimal['weights']}")


CASO 4: Inspeccionar Proveedores
================================

from data_fetcher_integration import display_data_provider_summary

tickers = ['AAPL', 'ALICORC1.HE', 'SPBLPGPT', 'TSLA', 'VOLCABC1.HE']

# Muestra qué proveedor se usará para cada ticker
display_data_provider_summary(tickers)

# Output:
# 🌐 Yahoo Finance (Mercados Globales)
#   Tickers: AAPL, TSLA
#
# 🇵🇪 BVL Data (Bolsa de Valores de Lima)
#   Tickers: ALICORC1.HE, VOLCABC1.HE
#
# 📊 Trading Economics (Índices Macro)
#   Tickers: SPBLPGPT
"""


# ==================== 6. CONFIGURACIÓN Y CREDENCIALES ====================

"""
OBTENCIÓN DE CREDENCIALES
=========================

1. BVL Data API
   ─────────────
   Website: https://www.bvl.com.pe
   Contacto: developer@bvl.com.pe
   
   Pasos:
   1. Registrarse en el portal de desarrolladores de BVL
   2. Crear una aplicación
   3. Generar API Key
   4. Guardar en variables de entorno
   
   Configuración en código:
   
       import os
       BVL_API_KEY = os.environ.get('BVL_API_KEY')
       fetcher = DataFetcher(bvl_api_key=BVL_API_KEY)

2. Trading Economics API
   ──────────────────────
   Website: https://tradingeconomics.com/api
   Plan: Free (limitado) o Subscription
   
   Pasos:
   1. Registrarse en Trading Economics
   2. Acceder a panel de desarrolladores
   3. Generar token API
   4. Guardar en variables de entorno
   
   Configuración en código:
   
       import os
       TE_TOKEN = os.environ.get('TRADING_ECONOMICS_TOKEN')
       fetcher = DataFetcher(trading_economics_token=TE_TOKEN)


CONFIGURACIÓN CON .env (RECOMENDADO)
====================================

Crear archivo .env en la raíz del proyecto:

    BVL_API_KEY=tu_clave_aqui
    TRADING_ECONOMICS_TOKEN=tu_token_aqui

Cargar en código:

    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    fetcher = DataFetcher(
        bvl_api_key=os.environ.get('BVL_API_KEY'),
        trading_economics_token=os.environ.get('TRADING_ECONOMICS_TOKEN')
    )
"""


# ==================== 7. MANEJO DE ERRORES ====================

"""
EXCEPCIONES Y RECUPERACIÓN
==========================

1. ConnectionError (Timeout)
   ────────────────────────
   Causa: API lenta o no disponible
   Manejo: Retry automático + logging
   
   Código interno en BVLDataProvider:
   
       try:
           response = self.session.get(url, timeout=10)
       except requests.exceptions.Timeout:
           logger.error("Timeout al conectar a BVL")
           return None  # Retorna DataFrame vacío

2. HTTPError (Unauthorized 401)
   ───────────────────────────
   Causa: API Key inválida o expirada
   Solución: Verificar credenciales
   
   Log: "Error HTTP en BVL: 401 - Unauthorized"

3. ValueError (Rango de fechas inválido)
   ────────────────────────────────────
   Causa: start_date > end_date o formato incorrecto
   Manejo: Validación en _validate_date_range()
   
   Ejemplo:
       try:
           data = provider.get_historical_data(
               'AAPL',
               start_date='2024-12-31',
               end_date='2024-01-01'  # ❌ Incorrecto
           )
       except ValueError as e:
           print(f"Error: {e}")

4. Empty DataFrame
   ───────────────
   Causa: No hay datos para el ticker/período
   Manejo: Retorna DataFrame vacío, warning en log
   
   Verificación:
       if data.empty:
           print("⚠️ No se pudieron descargar datos")


MEJORES PRÁCTICAS DE ERROR HANDLING
===================================

# ❌ MAL: Ignorar errores
data = provider.get_historical_data(ticker, start, end)

# ✅ BIEN: Verificar y manejar
data = provider.get_historical_data(ticker, start, end)
if data.empty:
    logger.warning(f"No hay datos para {ticker}")
    # Usar datos históricos, usar proxy, etc.

# ❌ MAL: Mismo try-except para todo
try:
    data = factory.fetch_data(tickers)
    portfolio = UnifiedPortfolioManager(data)
    result = portfolio.optimize_portfolio()
except Exception as e:
    print("Error!")

# ✅ BIEN: Errores específicos
try:
    data = factory.fetch_data(tickers)
except ValueError as e:
    logger.error(f"Datos inválidos: {e}")
    # Manejar específicamente
except ConnectionError as e:
    logger.error(f"Conexión fallida: {e}")
    # Reintentar
except Exception as e:
    logger.error(f"Error inesperado: {e}")
    raise
"""


# ==================== 8. TESTEO Y VALIDACIÓN ====================

"""
UNIT TESTS RECOMENDADOS
=======================

1. BaseDataProvider
   ────────────────
   ✓ _validate_date_range() con fechas válidas/inválidas
   ✓ _standardize_dataframe() con diferentes formatos
   ✓ Interfaz abstracta no pueda instanciarse

2. YahooFinanceProvider
   ────────────────────
   ✓ get_historical_data() para ticker válido
   ✓ get_historical_data() para ticker inválido
   ✓ Formato de salida cumple estándar
   ✓ Manejo de timeouts

3. BVLDataProvider
   ────────────────
   ✓ Conecta con API correctamente
   ✓ Autentica con API Key
   ✓ Mapeo correcto de columnas JSON → DataFrame
   ✓ Manejo de respuesta vacía
   ✓ Manejo de error 401 (API Key inválida)
   ✓ Manejo de error 404 (ticker no encontrado)

4. DataProviderFactory
   ────────────────────
   ✓ identify_market() para cada patrón
   ✓ get_provider() retorna clase correcta
   ✓ fetch_data() consolida múltiples tickers

5. Integración
   ──────────
   ✓ DataFetcher.fetch_data_dynamic() completo
   ✓ UnifiedPortfolioManager acepta datos consolidados
   ✓ Portfolio optimization sin errores


EJEMPLO DE TEST (pytest)
========================

import pytest
from data_providers import YahooFinanceProvider, DataProviderFactory

class TestDataProviders:
    
    def test_validate_date_range(self):
        from data_providers import BaseDataProvider
        
        start, end = BaseDataProvider._validate_date_range(
            '2024-01-01',
            '2024-12-31'
        )
        assert start == '2024-01-01'
        assert end == '2024-12-31'
    
    def test_validate_date_range_invalid(self):
        from data_providers import BaseDataProvider
        
        with pytest.raises(ValueError):
            BaseDataProvider._validate_date_range(
                '2024-12-31',
                '2024-01-01'  # start > end
            )
    
    def test_yahoo_provider_aapl(self):
        provider = YahooFinanceProvider()
        data = provider.get_historical_data(
            'AAPL',
            start_date='2024-01-01',
            end_date='2024-03-31'
        )
        
        assert not data.empty
        assert 'Close' in data.columns
        assert len(data) > 0
    
    def test_factory_identify_market(self):
        factory = DataProviderFactory()
        
        assert factory.identify_market('AAPL') == 'yahoo'
        assert factory.identify_market('ALICORC1.HE') == 'bvl'
        assert factory.identify_market('SPBLPGPT') == 'trading_economics'
"""


# ==================== 9. RENDIMIENTO Y OPTIMIZACIÓN ====================

"""
CONSIDERACIONES DE RENDIMIENTO
==============================

1. Descargas en Paralelo
   ──────────────────────
   Problema: Descargar múltiples tickers secuencialmente es lento
   
   Solución (futuro):
   
       from concurrent.futures import ThreadPoolExecutor
       
       def fetch_data_parallel(self, tickers):
           with ThreadPoolExecutor(max_workers=5) as executor:
               futures = {
                   executor.submit(
                       self.factory.get_provider(t).get_historical_data, t
                   ): t
                   for t in tickers
               }
               # Procesar resultados

2. Caché de Datos
   ───────────────
   Problema: API rate limits
   
   Solución:
   
       class CachedDataProvider(BaseDataProvider):
           def __init__(self, provider, cache_dir='./cache'):
               self.provider = provider
               self.cache_dir = cache_dir
           
           def get_historical_data(self, ticker, start_date, end_date):
               cache_key = f"{ticker}_{start_date}_{end_date}"
               # Verificar caché
               # Si existe, retornar
               # Si no, descargar y cachear

3. Rate Limiting
   ──────────────
   Implementar backoff exponencial:
   
       def _make_request_with_retry(self, url, max_retries=3):
           for i in range(max_retries):
               try:
                   return self.session.get(url, timeout=10)
               except RequestException:
                   wait_time = 2 ** i  # 1s, 2s, 4s
                   time.sleep(wait_time)
           raise ConnectionError("Max retries exceeded")


BENCHMARKS ESPERADOS
====================

Operación                    Tiempo esperado
─────────────────────────────────────────────
Descargar 5 tickers (YF)     2-3 segundos
Descargar 5 tickers (BVL)    3-5 segundos (depende API)
Factory routing (100 T)      < 100ms
DataFrame standardization    < 50ms
Portfolio optimization       1-2 segundos (según # activos)
"""


# ==================== 10. ROADMAP FUTURO ====================

"""
MEJORAS PLANIFICADAS
====================

Corto Plazo (1-2 meses):
─────────────────────
□ Descargas paralelas con ThreadPoolExecutor
□ Sistema de caché con SQLite
□ Retry automático con backoff exponencial
□ Soporte para more_itertools para manejo de timeouts
□ Tests unitarios completos

Mediano Plazo (3-6 meses):
──────────────────────────
□ WebSocket provider para datos en tiempo real
□ Soporte para opciones y futuros
□ API REST para exponer el sistema
□ Dashboard web (FastAPI + React)
□ Integración con base de datos (PostgreSQL)

Largo Plazo (6+ meses):
──────────────────────
□ Machine Learning para predicción de precios
□ Algoritmos de ejecución (VWAP, TWAP)
□ Backtesting avanzado con comisiones
□ Reporte interactivo con Plotly
□ Despliegue en cloud (AWS, GCP, Azure)


EXTENSIBILIDAD
==============

Agregar nuevo proveedor es simple:

1. Heredar de BaseDataProvider:

   class MyCustomProvider(BaseDataProvider):
       def get_historical_data(self, ticker, start_date, end_date, **kwargs):
           # Tu lógica aquí
           return self._standardize_dataframe(data)

2. Registrar en Factory:

   class DataProviderFactory:
       def __init__(self):
           self.custom_provider = MyCustomProvider()
       
       def identify_market(self, ticker):
           if ticker.startswith('CUSTOM_'):
               return 'custom'
           # ...

3. Usar:

   factory = DataProviderFactory()
   data = factory.fetch_data(['CUSTOM_TICKER1'])
"""


print(__doc__)
