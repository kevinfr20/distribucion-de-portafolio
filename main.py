"""
Sistema Integrado de Análisis y Optimización de Portafolios
===========================================================

Integra:
- unified_portfolio_colab.py (gestor principal)
- risk_metrics.py (cálculos avanzados de riesgo)
- backtesting.py (validación de estrategias)
- adaptive_optimization.py (optimización dinámica)
- ml_advanced_models.py (predicciones con ML)

Uso:
    python main.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings

# Importar módulos principales
from unified_portfolio_colab import DataFetcher, UnifiedPortfolioManager
from risk_metrics import AdvancedRiskMetrics, CorrelationAnalysis
from backtesting import AdvancedBacktester
from adaptive_optimization import AdaptivePortfolioOptimizer
from utils import DataProcessor, VisualizationUtils, Logger

warnings.filterwarnings('ignore')


class IntegratedPortfolioSystem:
    """Sistema integrado de análisis y optimización"""
    
    def __init__(self, tickers, start_date=None, end_date=None):
        """
        Inicializa el sistema integrado
        
        Parameters:
        -----------
        tickers : list
            Lista de tickers
        start_date : str
            Fecha inicio (YYYY-MM-DD)
        end_date : str
            Fecha fin (YYYY-MM-DD)
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n{'='*80}")
        print(f"🚀 SISTEMA INTEGRADO DE ANÁLISIS DE PORTAFOLIOS")
        print(f"{'='*80}")
        
        # Descargar datos
        print(f"\n📥 Descargando datos...")
        fetcher = DataFetcher()
        self.prices = fetcher.fetch_data(tickers, start_date=start_date, end_date=end_date)
        
        if self.prices.empty:
            raise ValueError("❌ No se pudieron descargar datos.")
        
        print(f"✅ Datos descargados: {self.prices.shape[0]} días, {self.prices.shape[1]} activos")
        
        self.tickers = tickers
        self.returns = self.prices.pct_change().dropna()
        
        # Inicializar managers
        self.manager = UnifiedPortfolioManager(self.prices)
        self.risk_metrics = AdvancedRiskMetrics(self.returns)
        self.correlation_analysis = CorrelationAnalysis(self.returns)
        self.backtester = AdvancedBacktester(self.prices, self.returns)
        self.adaptive_optimizer = AdaptivePortfolioOptimizer(self.prices, self.returns)
    
    def run_full_analysis(self, initial_capital=100000):
        """
        Ejecuta un análisis completo del portafolio
        
        Parameters:
        -----------
        initial_capital : float
            Capital inicial para backtesting
        """
        
        # 1. ANÁLISIS DE RIESGO
        print(f"\n{'='*80}")
        print(f"⚠️ ANÁLISIS AVANZADO DE RIESGO")
        print(f"{'='*80}")
        
        risk_summary = self.risk_metrics.get_risk_summary()
        Logger.log_metrics(risk_summary, "📊 Métricas de Riesgo")
        
        # 2. ANÁLISIS DE CORRELACIÓN
        print(f"\n{'='*80}")
        print(f"🔗 ANÁLISIS DE CORRELACIÓN")
        print(f"{'='*80}")
        
        corr_matrix = self.correlation_analysis.get_average_correlation()
        print(f"\nMatriz de Correlación:")
        print(corr_matrix.round(3))
        
        # 3. OPTIMIZACIÓN
        print(f"\n{'='*80}")
        print(f"🎯 OPTIMIZACIÓN DE PORTAFOLIO")
        print(f"{'='*80}")
        
        optimal_weights = self.manager.optimize_portfolio('sharpe', update_self_weights=True)
        Logger.log_metrics(
            {**optimal_weights, 'weights': dict(zip(self.tickers, optimal_weights['weights'].values()))},
            "✅ Portafolio Óptimo (Máximo Sharpe)"
        )
        
        # 4. DETECCIÓN DE RÉGIMEN
        print(f"\n{'='*80}")
        print(f"📈 DETECCIÓN DE RÉGIMEN DE MERCADO")
        print(f"{'='*80}")
        
        regime = self.adaptive_optimizer.detect_market_regime()
        Logger.log_metrics(regime, f"\n🔍 Régimen Actual: {regime['regime']}")
        
        # 5. BACKTESTING WALK-FORWARD
        print(f"\n{'='*80}")
        print(f"📊 BACKTESTING CON WALK-FORWARD ANALYSIS")
        print(f"{'='*80}")
        
        def weights_func(returns):
            mean_ret = returns.mean()
            std_ret = returns.std()
            weights = (mean_ret / (std_ret + 0.001)) ** 2
            return weights / weights.sum()
        
        bt_results = self.backtester.walk_forward_backtest(weights_func)
        Logger.log_metrics(
            {
                'total_periods': bt_results['total_positions'],
                'average_return': bt_results['average_return'],
                'average_volatility': bt_results['average_volatility'],
                'average_sharpe': bt_results['average_sharpe']
            },
            "📈 Resultados Walk-Forward"
        )
        
        # 6. ANÁLISIS POR RÉGIMEN DE MERCADO
        print(f"\n{'='*80}")
        print(f"🎯 ANÁLISIS POR RÉGIMEN DE MERCADO")
        print(f"{'='*80}")
        
        regime_results = self.backtester.market_regime_backtest(
            optimal_weights['weights'],
            initial_capital=initial_capital
        )
        print(f"\nRendimiento Mercado Alcista:")
        Logger.log_metrics(regime_results['bull_market'])
        print(f"\nRendimiento Mercado Bajista:")
        Logger.log_metrics(regime_results['bear_market'])
        
        # 7. STRESS TESTING
        print(f"\n{'='*80}")
        print(f"⚠️ STRESS TESTING")
        print(f"{'='*80}")
        
        stress_results = self.manager.stress_test()
        for scenario, metrics in stress_results.items():
            Logger.log_metrics(metrics, f"\n📉 Escenario: {scenario}")
        
        print(f"\n{'='*80}")
        print(f"✅ ANÁLISIS COMPLETO FINALIZADO")
        print(f"{'='*80}\n")
        
        return {
            'risk_summary': risk_summary,
            'optimal_weights': optimal_weights,
            'regime': regime,
            'backtest_results': bt_results,
            'regime_analysis': regime_results,
            'stress_test': stress_results
        }


if __name__ == "__main__":
    # Configuración
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    start_date = '2023-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    initial_capital = 100000
    
    try:
        # Ejecutar sistema integrado
        system = IntegratedPortfolioSystem(tickers, start_date, end_date)
        results = system.run_full_analysis(initial_capital)
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
