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
    google colab main.py
"""

import sys
sys.path.append("/content/distribucion-de-portafolio")

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
from IPython.display import display, Markdown

# Importar m3dulos principales
from unified_portfolio_colab import DataFetcher, UnifiedPortfolioManager
from risk_metrics import AdvancedRiskMetrics, CorrelationAnalysis
from backtesting import AdvancedBacktester
from adaptive_optimization import AdaptivePortfolioOptimizer
from utils import DataProcessor, VisualizationUtils, Logger

warnings.filterwarnings("ignore")

class IntegratedPortfolioSystem:
    """Sistema integrado de an1lisis y optimizaci3n"""

    def __init__(self, tickers, start_date=None, end_date=None):
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        print(f"\n{'='*80}")
        print(f"🚀 SISTEMA INTEGRADO DE AN1LISIS DE PORTAFOLIOS")
        print(f"{'='*80}")

        fetcher = DataFetcher()
        self.prices = fetcher.fetch_data(tickers, start_date)

        if self.prices.empty:
            raise ValueError("❌ No se pudieron descargar datos.")

        print(f"✅ Datos descargados: {self.prices.shape[0]} días, {self.prices.shape[1]} activos")
        
        self.tickers = tickers
        self.returns = self.prices.pct_change().dropna()
        self.manager = UnifiedPortfolioManager(self.prices)
        self.risk_metrics = AdvancedRiskMetrics(self.returns)
        self.correlation_analysis = CorrelationAnalysis(self.returns)
        self.backtester = AdvancedBacktester(self.prices, self.returns)
        self.adaptive_optimizer = AdaptivePortfolioOptimizer(self.prices, self.returns)

    def run_full_analysis(self, initial_capital=100000):
        # 1. AN1LISIS DE RIESGO
        print(f"\n{'='*80}")
        print(f"⚠️ AN1LISIS AVANZADO DE RIESGO")
        print(f"{'='*80}")
        risk_summary = self.risk_metrics.get_risk_summary()
        Logger.log_metrics(risk_summary, "📊 M3tricas de Riesgo")

        # 2. AN1LISIS DE CORRELACI3N
        print(f"\n{'='*80}")
        print(f"🔗 AN1LISIS DE CORRELACI3N")
        print(f"{'='*80}")
        corr_matrix = self.correlation_analysis.get_average_correlation()
        display(corr_matrix.round(3))

        # 3. OPTIMIZACI3N
        print(f"\n{'='*80}")
        print(f"🎯 OPTIMIZACI3N DE PORTAFOLIO")
        print(f"{'='*80}")
        optimal_results = self.manager.optimize_portfolio("sharpe", update_self_weights=True)
        weights_df = pd.DataFrame(list(optimal_results['weights'].items()), columns=['Ticker', 'Weight'])
        weights_df['Weight'] = weights_df['Weight'].apply(lambda x: f"{x*100:.2f}%")
        display(Markdown("### ✅ Pesos 3ptimos de Portafolio"))
        display(weights_df)

        # 4. DETECCI3N DE R3GIMEN
        print(f"\n{'='*80}")
        print(f"📈 DETECCI3N DE R3GIMEN DE MERCADO")
        print(f"{'='*80}")
        regime = self.adaptive_optimizer.detect_market_regime()
        Logger.log_metrics(regime, f"🔍 R3gimen Actual: {regime['regime']}")

        # 5. BACKTESTING
        print(f"\n{'='*80}")
        print(f"📊 BACKTESTING CON WALK-FORWARD ANALYSIS")
        print(f"{'='*80}")
        def weights_func(returns):
            mean_ret = returns.mean()
            std_ret = returns.std()
            weights = (mean_ret / (std_ret + 0.001)) ** 2
            return weights / weights.sum()
        
        bt_results = self.backtester.walk_forward_backtest(weights_func)
        
        # Formatear resultados de backtesting para visualizaci3n
        bt_display = pd.DataFrame({
            'M3trica': ['Retorno Promedio', 'Volatilidad Promedio', 'Sharpe Promedio', 'Total Posiciones'],
            'Valor': [
                f"{bt_results['average_return']*100:.2f}%", 
                f"{bt_results['average_volatility']*100:.2f}%", 
                f"{bt_results['average_sharpe']:.4f}",
                str(bt_results['total_positions'])
            ]
        })
        display(Markdown("### 📈 Resultados del Backtest"))
        display(bt_display)

        # 7. STRESS TESTING
        print(f"\n{'='*80}")
        print(f"⚠️ STRESS TESTING")
        print(f"{'='*80}")
        stress_results = self.manager.stress_test()
        for scenario, metrics in stress_results.items():
            Logger.log_metrics(metrics, f"📉 Escenario: {scenario}")

        print(f"\n{'='*80}")
        print(f"✅ AN1LISIS COMPLETO FINALIZADO")
        print(f"{'='*80}\n")

        return {
            "risk_summary": risk_summary,
            "optimal_weights": optimal_results['weights'],
            "regime": regime,
            "backtest_results": bt_results,
            "stress_test": stress_results
        }

if __name__ == "__main__":
    tickers = ["BAP", "ENGIEC1", "UNACEMC1", "BBVAC1", "CREDITC1", "ORYGENC1", "IFS", "FERREYC1", "NEXAPEC1", "INRETC1", "CARTAVC1", "ALICORC1", "CVERDEC1", "AUNA", "PLUZENC1", "CORAREI1", "ATACOBC1", "IPCHBC1"]
    start_date = "2021-04-02"
    try:
        system = IntegratedPortfolioSystem(tickers, start_date)
        results = system.run_full_analysis(2050)
    except Exception as e:
        print(f"Error: {e}")
