"""
Módulo de Integración: Nuevos Proveedores de Datos con UnifiedPortfolioManager

Este módulo demuestra cómo integrar el sistema de proveedores de datos refactorizado
(data_providers.py) con el UnifiedPortfolioManager existente en unified_portfolio_colab.py

Proporciona un wrapper DataFetcher mejorado que mantiene compatibilidad hacia atrás
mientras aprovecha la nueva arquitectura de proveedores.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
import logging
<<<<<<< Updated upstream
from data_providers import BVLDataProvider
from data_providers import LocalCSVProvider

=======
>>>>>>> Stashed changes

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== WRAPPER: DATA FETCHER MEJORADO ====================
class PortfolioOptimizer:
    def __init__(self):
        self.data_provider = BVLDataProvider()  # Automático con fallback
    
    def optimize(self, tickers: list):
        for ticker in tickers:
            # ¡Sin cambios! El fallback es automático
            df = self.data_provider.get_historical_data(
                ticker=ticker,
                start_date=...,
                end_date=...
            )
class DataFetcher:
    """
    Wrapper mejorado del DataFetcher original que integra el sistema de proveedores.

    Mantiene compatibilidad con código existente mientras proporciona soporte para
    múltiples fuentes de datos (Yahoo Finance, BVL, Trading Economics).

    Diferencias con la versión anterior:
    - Usa DataProviderFactory internamente
    - Identifica automáticamente la fuente correcta por ticker
    - Soporta activos peruanos de BVL
    - Mejor manejo de errores
    """

    def __init__(
        self,
        bvl_api_key: Optional[str] = None,
        trading_economics_token: Optional[str] = None,
    ):
        """
        Inicializa el DataFetcher mejorado.

        Parameters:
        -----------
        bvl_api_key : str, optional
            Clave API para autenticación en BVL Data
        trading_economics_token : str, optional
            Token API para Trading Economics

        Example:
        --------
        # Uso sin credenciales (Yahoo Finance por defecto)
        fetcher = DataFetcher()

        # Uso con credenciales de BVL
        fetcher = DataFetcher(bvl_api_key='tu_api_key')
        """
        self.factory = DataProviderFactory(
            bvl_api_key=bvl_api_key, trading_economics_token=trading_economics_token
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def fetch_data(
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_dividends: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Descarga datos históricos para múltiples tickers (INTERFAZ ESTÁTICA - COMPATIBLE).

        Este método mantiene la interfaz estática original para compatibilidad hacia atrás.
        Internamente utiliza la factoría de proveedores para enrutar a la fuente correcta.

        Parameters:
        -----------
        tickers : list
            Lista de tickers (ej: ['AAPL', 'ALICORC1.HE', 'SPBLPGPT'])
        start_date : str, optional
            Fecha inicio en formato YYYY-MM-DD
        end_date : str, optional
            Fecha fin en formato YYYY-MM-DD
        include_dividends : bool, optional
            Si es True, intenta incluir dividendos (solo Yahoo Finance soporta esto)
        **kwargs : dict
            Parámetros adicionales para proveedores específicos

        Returns:
        --------
        pd.DataFrame
            DataFrame con precios ajustados/cierre consolidados

        Nota:
        -----
        Para compatibilidad con código existente, este método devuelve un único DataFrame.
        Si necesitas dividendos, usa la instancia: fetcher_instance.fetch_data_with_dividends()

        Example:
        --------
        # Descargar múltiples tickers de diferentes mercados
        prices = DataFetcher.fetch_data(
            ['AAPL', 'ALICORC1.HE', 'SPBLPGPT'],
            start_date='2023-01-01',
            end_date='2024-12-31'
        )
        """
        # Crear instancia temporal para usar la factoría
        fetcher = DataFetcher()
        return fetcher.fetch_data_dynamic(
            tickers, start_date, end_date, include_dividends, **kwargs
        )

    def fetch_data_dynamic(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_dividends: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Versión instancia de fetch_data que puede reutilizar la factoría.

        Parameters:
        -----------
        tickers : list
            Lista de tickers
        start_date : str, optional
            Fecha inicio
        end_date : str, optional
            Fecha fin
        include_dividends : bool, optional
            Incluir dividendos (solo Yahoo Finance)
        **kwargs : dict
            Parámetros adicionales

        Returns:
        --------
        pd.DataFrame
            Datos consolidados
        """
        if not tickers:
            self.logger.warning("⚠️ Lista de tickers vacía")
            return pd.DataFrame()

        self.logger.info(f"📥 Descargando datos para {tickers}...")

        # Agrupar tickers por mercado
        tickers_by_market = self._group_tickers_by_market(tickers)
        all_data = {}

        # Descargar datos de cada mercado
        for market, market_tickers in tickers_by_market.items():
            self.logger.info(
                f"   Procesando {len(market_tickers)} ticker(s) de {market}..."
            )

            for ticker in market_tickers:
                provider = self.factory.get_provider(ticker)
                data = provider.get_historical_data(
                    ticker, start_date, end_date, **kwargs
                )

                if not data.empty:
                    # Para compatibilidad, usar Close como serie de precios
                    all_data[ticker] = data["Close"]
                else:
                    self.logger.warning(
                        f"   ⚠️ No se pudieron descargar datos para {ticker}"
                    )

        # Consolidar datos
        if all_data:
            consolidated = pd.DataFrame(all_data)
            self.logger.info(
                f"✅ {len(consolidated)} registros descargados para {len(all_data)} activo(s)"
            )
            return consolidated
        else:
            self.logger.error(
                f"❌ No se pudieron descargar datos para ninguno de los tickers"
            )
            return pd.DataFrame()

    def fetch_data_with_dividends(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Descarga datos históricos incluyendo dividendos (solo Yahoo Finance).

        Parameters:
        -----------
        tickers : list
            Lista de tickers
        start_date : str, optional
            Fecha inicio
        end_date : str, optional
            Fecha fin
        **kwargs : dict
            Parámetros adicionales

        Returns:
        --------
        tuple : (prices_df, dividends_df)
            - prices_df: DataFrame con precios de cierre
            - dividends_df: DataFrame con dividendos

        Note:
        -----
        Esta función solo funciona con Yahoo Finance. Para tickers de BVL o
        Trading Economics, los dividendos no están disponibles.
        """
        # Nota: Esta es una función de utilidad. En producción, solo Yahoo Finance
        # proporciona dividendos. BVL Data y Trading Economics no incluyen esta información.
        self.logger.warning(
            "⚠️ dividends solo disponibles para Yahoo Finance. Otros mercados retornarán DataFrame vacío."
        )

        prices = self.fetch_data_dynamic(tickers, start_date, end_date)
        dividends = pd.DataFrame()  # Placeholder

        return prices, dividends

    def _group_tickers_by_market(self, tickers: List[str]) -> dict:
        """
        Agrupa tickers por su mercado de origen.

        Parameters:
        -----------
        tickers : list
            Lista de tickers a agrupar

        Returns:
        --------
        dict
            Diccionario {market: [tickers]}
        """
        grouped = {}
        for ticker in tickers:
            market = self.factory.identify_market(ticker)
            if market not in grouped:
                grouped[market] = []
            grouped[market].append(ticker)
        return grouped

    def get_market_info(self, tickers: List[str]) -> dict:
        """
        Proporciona información sobre qué proveedor se usará para cada ticker.

        Parameters:
        -----------
        tickers : list
            Lista de tickers

        Returns:
        --------
        dict
            Información de mercado para cada ticker

        Example:
        --------
        >>> fetcher = DataFetcher()
        >>> info = fetcher.get_market_info(['AAPL', 'ALICORC1.HE', 'SPBLPGPT'])
        >>> for ticker, data in info.items():
        ...     print(f"{ticker}: {data['market']} ({data['provider']})")
        """
        info = {}
        for ticker in tickers:
            market = self.factory.identify_market(ticker)
            provider = self.factory.get_provider(ticker)
            info[ticker] = {"market": market, "provider": provider.provider_name}
        return info


# ==================== FUNCIONES AUXILIARES DE INTEGRACIÓN ====================
def create_portfolio_from_mixed_tickers(
    tickers: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    weights: Optional[List[float]] = None,
    bvl_api_key: Optional[str] = None,
    trading_economics_token: Optional[str] = None,
):
    """
    Función auxiliar para crear un portafolio con tickers de múltiples mercados.

    Parameters:
    -----------
    tickers : list
        Lista de tickers (Yahoo Finance, BVL, Trading Economics)
    start_date : str, optional
        Fecha inicio
    end_date : str, optional
        Fecha fin
    weights : list, optional
        Pesos del portafolio. Si no se especifican, usa pesos iguales.
    bvl_api_key : str, optional
        Clave API para BVL
    trading_economics_token : str, optional
        Token para Trading Economics

    Returns:
    --------
    UnifiedPortfolioManager
        Gestor de portafolios inicializado

    Example:
    --------
    from unified_portfolio_colab import UnifiedPortfolioManager

    # Portafolio mixto
    portfolio = create_portfolio_from_mixed_tickers(
        tickers=['AAPL', 'MSFT', 'ALICORC1.HE', 'VOLCABC1.HE'],
        start_date='2023-01-01',
        end_date='2024-12-31',
        weights=[0.3, 0.3, 0.2, 0.2]
    )
    """
    # Importar aquí para evitar dependencias circulares
    try:
        from unified_portfolio_colab import UnifiedPortfolioManager
    except ImportError:
        raise ImportError(
            "unified_portfolio_colab.py debe estar en el mismo directorio"
        )

    # Crear fetcher con credenciales
    fetcher = DataFetcher(
        bvl_api_key=bvl_api_key, trading_economics_token=trading_economics_token
    )

    # Descargar datos
    prices = fetcher.fetch_data_dynamic(tickers, start_date, end_date)

    if prices.empty:
        raise ValueError(
            "No se pudieron descargar datos para los tickers especificados"
        )

    # Crear y retornar portafolio
    portfolio = UnifiedPortfolioManager(prices, weights=weights)
    return portfolio


def display_data_provider_summary(tickers: List[str]):
    """
    Muestra un resumen de qué proveedor se usará para cada ticker.

    Parameters:
    -----------
    tickers : list
        Lista de tickers

    Example:
    --------
    display_data_provider_summary(['AAPL', 'ALICORC1.HE', 'SPBLPGPT'])
    """
    fetcher = DataFetcher()
    info = fetcher.get_market_info(tickers)

    print("\n" + "=" * 80)
    print("📊 RESUMEN DE PROVEEDORES DE DATOS")
    print("=" * 80 + "\n")

    # Agrupar por mercado
    by_market = {}
    for ticker, data in info.items():
        market = data["market"]
        if market not in by_market:
            by_market[market] = []
        by_market[market].append(ticker)

    # Mostrar información
    market_names = {
        "yahoo": "🌐 Yahoo Finance (Mercados Globales)",
        "bvl": "🇵🇪 BVL Data (Bolsa de Valores de Lima)",
        "trading_economics": "📊 Trading Economics (Índices Macro)",
    }

    for market, tickers_in_market in by_market.items():
        print(f"{market_names.get(market, market)}")
        print(f"  Tickers: {', '.join(tickers_in_market)}")
        print()

    print("=" * 80 + "\n")


# ==================== EJEMPLO DE USO COMPLETO ====================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 INTEGRACIÓN: NUEVOS PROVEEDORES + PORTFOLIO MANAGER")
    print("=" * 80 + "\n")

    # ==================== PARTE 1: DEMOSTRACIÓN DE ENRUTAMIENTO ====================
    print("PARTE 1: IDENTIFICACIÓN AUTOMÁTICA DE PROVEEDORES")
    print("-" * 80 + "\n")

    test_tickers = [
        "AAPL",  # Yahoo Finance
        "MSFT",  # Yahoo Finance
        "ALICORC1.HE",  # BVL
        "VOLCABC1.HE",  # BVL
        "SPBLPGPT",  # Trading Economics
    ]

    display_data_provider_summary(test_tickers)

    # ==================== PARTE 2: DESCARGA DE DATOS ====================
    print("PARTE 2: DESCARGA DE DATOS (Ejemplo: Solo AAPL y MSFT)")
    print("-" * 80 + "\n")

    fetcher = DataFetcher()

    # Descargar datos de ejemplo (solo Yahoo Finance por simplicidad sin credenciales)
    print("Descargando datos de activos globales...\n")
    prices = fetcher.fetch_data_dynamic(
        ["AAPL", "MSFT"], start_date="2024-01-01", end_date="2024-03-31"
    )

    if not prices.empty:
        print(f"\n✅ Datos descargados exitosamente")
        print(f"   Forma: {prices.shape}")
        print(f"   Columnas: {list(prices.columns)}")
        print(f"\n📋 Primeras 5 filas:\n{prices.head()}")
        print(f"\n📊 Últimas 5 filas:\n{prices.tail()}")
        print(f"\n📈 Estadísticas:\n{prices.describe()}")
    else:
        print("⚠️ No se pudieron descargar los datos")

    # ==================== PARTE 3: INTEGRACIÓN CON PORTFOLIO MANAGER ====================
    print("\n\nPARTE 3: INTEGRACIÓN CON UNIFIED PORTFOLIO MANAGER")
    print("-" * 80 + "\n")

    if not prices.empty:
        try:
            # Importar el manager
            import sys
            import os

            # Intenta importar el UnifiedPortfolioManager
            try:
                from unified_portfolio_colab import UnifiedPortfolioManager

                # Crear portafolio con pesos iguales
                portfolio = UnifiedPortfolioManager(prices)

                print("✅ Portafolio creado exitosamente\n")

                # Mostrar resumen
                summary = portfolio.get_portfolio_summary()
                print("📋 RESUMEN DEL PORTAFOLIO:")
                print(f"   Activos: {summary['assets']}")
                print(f"   Pesos: {summary['weights']}")
                print(
                    f"   Retorno esperado (anualizado): {summary['expected_return']*100:.2f}%"
                )
                print(f"   Volatilidad (anualizada): {summary['volatility']*100:.2f}%")
                print(f"   Sharpe Ratio: {summary['sharpe_ratio']:.4f}")
                print(f"   Máximo Drawdown: {summary['max_drawdown']*100:.2f}%")

                # Optimizar para máximo Sharpe
                print("\n🎯 OPTIMIZANDO PARA MÁXIMO SHARPE...\n")
                optimal = portfolio.optimize_portfolio(
                    "sharpe", update_self_weights=True
                )
                print("✅ Optimización completada")
                print(f"   Pesos óptimos: {optimal['weights']}")
                print(f"   Retorno esperado: {optimal['expected_return']*100:.2f}%")
                print(f"   Volatilidad: {optimal['volatility']*100:.2f}%")
                print(f"   Sharpe Ratio: {optimal['sharpe_ratio']:.4f}")

            except ImportError as e:
                print(f"⚠️ No se puede importar UnifiedPortfolioManager: {e}")
                print(
                    "   (Asegúrate de que unified_portfolio_colab.py está disponible)"
                )

        except Exception as e:
            print(f"❌ Error durante la integración: {e}")
            import traceback

            traceback.print_exc()

    # ==================== PARTE 4: INFORMACIÓN SOBRE CREDENCIALES ====================
    print("\n\n" + "=" * 80)
    print("📝 CONFIGURACIÓN PARA PRODUCCIÓN")
    print("=" * 80 + "\n")

    print("""
Para usar BVL Data y Trading Economics en producción, configura las credenciales:

1. BVL Data API:
   - Contacta a: https://www.bvl.com.pe
   - Obtén tu API Key
   - Úsalo: fetcher = DataFetcher(bvl_api_key='tu_clave')

2. Trading Economics API:
   - Contacta a: https://tradingeconomics.com/api
   - Obtén tu Token
   - Úsalo: fetcher = DataFetcher(trading_economics_token='tu_token')

3. En el código:
   
   # Ejemplo con credenciales
   fetcher = DataFetcher(
       bvl_api_key='tu_api_key_bvl',
       trading_economics_token='tu_token_te'
   )
   
   # Descargar datos peruanos
   prices = fetcher.fetch_data_dynamic(
       ['ALICORC1.HE', 'VOLCABC1.HE', 'FERREYCORP1.HE'],
       start_date='2023-01-01',
       end_date='2024-12-31'
   )
   
   # Crear portafolio
   from unified_portfolio_colab import UnifiedPortfolioManager
   portfolio = UnifiedPortfolioManager(prices)
""")

    print("=" * 80 + "\n")
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("=" * 80 + "\n")
