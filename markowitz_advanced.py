import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
import yfinance as yf
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# ==================== DATA FETCHER ====================

class DataFetcher:
    """Descarga datos históricos de Yahoo Finance"""

    @staticmethod
    def fetch_data(tickers, start_date=None, end_date=None, include_dividends=False):
        """Descarga precios históricos"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        print(f"📥 Descargando datos para {tickers}...")
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)

        if data.empty:
            print(f"❌ Error: No se pudieron descargar datos para {tickers} desde {start_date} hasta {end_date}. Por favor, revise los tickers o el rango de fechas. Retornando DataFrame vacío.")
            return pd.DataFrame()

        close_data = None
        if isinstance(data.columns, pd.MultiIndex):
            if 'Close' in data.columns.get_level_values(0):
                close_data = data['Close']
            else:
                print(f"❌ Error: La columna 'Close' no se encontró en el nivel principal de los datos MultiIndex para {tickers}. Columnas disponibles (nivel 0): {data.columns.get_level_values(0).unique().tolist()}")
                return pd.DataFrame()
        elif 'Close' in data.columns:
            close_data = data['Close']
        else:
            print(f"❌ Error: La columna 'Close' no se encontró en los datos descargados para {tickers}. Columnas disponibles: {data.columns.tolist()}")
            return pd.DataFrame()

        if include_dividends:
            print("ℹ️ Note: Dividend handling not fully implemented in optimizer for direct dividend yields. Using adjusted close.")
        return close_data


# ==================== MARKOWITZ OPTIMIZER ====================

class AdvancedMarkowitzOptimizer:
    """Optimizador basado en Teoría de Markowitz"""

    def __init__(self, prices, risk_free_rate=0.02):
        """
        Inicializa el optimizador

        Teoría de Markowitz:
        - Maximiza retorno para un nivel de riesgo
        - Minimiza riesgo para un nivel de retorno
        - Considera correlación entre activos
        """
        self.prices = prices
        self.risk_free_rate = risk_free_rate

        # Retornos diarios
        self.returns = prices.pct_change().dropna()
        self.cov_matrix = self.returns.cov()
        self.mean_returns = self.returns.mean()

        # Anualizados
        self.annual_mean_returns = self.mean_returns * 252
        self.annual_cov_matrix = self.cov_matrix * 252

    # ==================== FUNCIONES DE CÁLCULO ====================

    def calculate_portfolio_return(self, weights):
        """Retorno esperado del portafolio"""
        return np.sum(self.annual_mean_returns * weights)

    def calculate_portfolio_std(self, weights):
        """Volatilidad del portafolio"""
        return np.sqrt(np.dot(weights.T, np.dot(self.annual_cov_matrix, weights)))

    def calculate_sharpe_ratio(self, weights):
        """Índice de Sharpe = Retorno / Riesgo"""
        ret = self.calculate_portfolio_return(weights)
        std = self.calculate_portfolio_std(weights)
        return (ret - self.risk_free_rate) / std if std > 0 else 0

    # ==================== OPTIMIZACIONES ====================

    def optimize_sharpe_ratio(self):
        """Máximo Sharpe Ratio - Portafolio Óptimo de Markowitz"""
        print("🎯 Optimizando para máximo Sharpe Ratio...\n")

        n = len(self.prices.columns)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},)
        bounds = tuple((0, 1) for _ in range(n))
        init_weights = np.array([1/n] * n)

        result = minimize(
            lambda w: -self.calculate_sharpe_ratio(w),
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        weights = result.x
        return {
            'weights': dict(zip(self.prices.columns, weights)),
            'return': self.calculate_portfolio_return(weights),
            'volatility': self.calculate_portfolio_std(weights),
            'sharpe': self.calculate_sharpe_ratio(weights)
        }

    def optimize_min_volatility(self):
        """Mínima Volatilidad - Portafolio Defensivo"""
        print("🎯 Optimizando para mínima volatilidad...\n")

        n = len(self.prices.columns)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},)
        bounds = tuple((0, 1) for _ in range(n))
        init_weights = np.array([1/n] * n)

        result = minimize(
            lambda w: self.calculate_portfolio_std(w),
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        weights = result.x
        return {
            'weights': dict(zip(self.prices.columns, weights)),
            'return': self.calculate_portfolio_return(weights),
            'volatility': self.calculate_portfolio_std(weights),
            'sharpe': self.calculate_sharpe_ratio(weights)
        }

    def optimize_efficient_frontier(self, num_points=50):
        """Frontera Eficiente de Markowitz"""
        print(f"📈 Generando Frontera Eficiente con {num_points} puntos...\n")

        n = len(self.prices.columns)
        min_ret = self.annual_mean_returns.min()
        max_ret = self.annual_mean_returns.max()
        target_returns = np.linspace(min_ret, max_ret, num_points)

        frontier = []

        for target in target_returns:
            constraints = (
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: self.calculate_portfolio_return(x) - target}
            )
            bounds = tuple((0, 1) for _ in range(n))
            init_weights = np.array([1/n] * n)

            try:
                result = minimize(
                    lambda w: self.calculate_portfolio_std(w),
                    init_weights,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints
                )

                if result.success:
                    frontier.append({
                        'return': self.calculate_portfolio_return(result.x),
                        'volatility': self.calculate_portfolio_std(result.x),
                        'sharpe': self.calculate_sharpe_ratio(result.x)
                    })
            except:
                pass

        return frontier

    # ==================== VISUALIZACIONES ====================

    def plot_efficient_frontier(self):
        """Gráfica de Frontera Eficiente"""
        frontier = self.optimize_efficient_frontier(50)
        max_sharpe = self.optimize_sharpe_ratio()
        min_vol = self.optimize_min_volatility()

        fig, ax = plt.subplots(figsize=(14, 8))

        # Frontera
        f_returns = [p['return'] for p in frontier]
        f_vols = [p['volatility'] for p in frontier]
        f_sharpes = [p['sharpe'] for p in frontier]

        scatter = ax.scatter(f_vols, f_returns, c=f_sharpes, cmap='viridis',
                           s=100, alpha=0.6, edgecolors='black')

        # Máximo Sharpe
        ax.scatter(max_sharpe['volatility'], max_sharpe['return'],
                  marker='*', color='red', s=1000, edgecolors='black', linewidth=2,
                  label='Máximo Sharpe', zorder=5)

        # Mínima Volatilidad
        ax.scatter(min_vol['volatility'], min_vol['return'],
                  marker='s', color='orange', s=200, edgecolors='black', linewidth=2,
                  label='Mínima Volatilidad', zorder=5)

        ax.set_xlabel('Volatilidad (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Retorno Esperado (%)', fontsize=12, fontweight='bold')
        ax.set_title('📈 Frontera Eficiente de Markowitz', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)

        plt.colorbar(scatter, ax=ax, label='Sharpe Ratio')
        plt.tight_layout()
        return fig

    def plot_weights(self):
        """Gráfica de pesos"""
        max_sharpe = self.optimize_sharpe_ratio()

        fig, ax = plt.subplots(figsize=(10, 6))
        weights = list(max_sharpe['weights'].values())
        assets = list(max_sharpe['weights'].keys())

        colors = plt.cm.Set3(np.linspace(0, 1, len(assets)))
        ax.pie(weights, labels=assets, autopct='%1.1f%%', colors=colors,
              startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})

        ax.set_title('🎯 Pesos Óptimos del Portafolio', fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig

    def print_summary(self):
        """Imprime resumen"""
        print("\n" + "="*80)
        print("📊 OPTIMIZACIÓN DE PORTAFOLIO - TEORÍA DE MARKOWITZ")
        print("="*80 + "\n")

        max_sharpe = self.optimize_sharpe_ratio()
        min_vol = self.optimize_min_volatility()

        print("🎯 PORTAFOLIO ÓPTIMO (MÁXIMO SHARPE RATIO)\n")
        print("PESOS:")
        for ticker, weight in max_sharpe['weights'].items():
            print(f"  {ticker}: {weight*100:>6.2f}%")

        print(f"\nMÉTRICAS:")
        print(f"  Retorno Esperado:  {max_sharpe['return']*100:>7.2f}%")
        print(f"  Volatilidad:       {max_sharpe['volatility']*100:>7.2f}%")
        print(f"  Sharpe Ratio:      {max_sharpe['sharpe']:>7.4f}")

        print("\n" + "-"*80)
        print("🛡️  PORTAFOLIO DEFENSIVO (MÍNIMA VOLATILIDAD)\n")
        print("PESOS:")
        for ticker, weight in min_vol['weights'].items():
            print(f"  {ticker}: {weight*100:>6.2f}%")

        print(f"\nMÉTRICAS:")
        print(f"  Retorno Esperado:  {min_vol['return']*100:>7.2f}%")
        print(f"  Volatilidad:       {min_vol['volatility']*100:>7.2f}%")
        print(f"  Sharpe Ratio:      {min_vol['sharpe']:>7.4f}")
        print("\n" + "="*80 + "\n")


# ==================== EJEMPLO ====================

if __name__ == "__main__":
    print("\n🚀 OPTIMIZADOR DE PORTAFOLIO - TEORÍA DE MARKOWITZ\n")

    # Descargar datos de ejemplo
    fetcher = DataFetcher()
    tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN'] # Ejemplo de tickers
    prices = fetcher.fetch_data(tickers)

    # Check if prices DataFrame is empty before proceeding
    if not prices.empty:
        # Optimizar
        optimizer = AdvancedMarkowitzOptimizer(prices)
        optimizer.print_summary()

        # Gráficas
        optimizer.plot_efficient_frontier()
        optimizer.plot_weights()
        plt.show()
    else:
        print("No se pudo proceder con la optimización debido a la falta de datos.")

# The following example code uses methods (optimize_with_constraints, backtest_portfolio, compare_with_benchmark)
# and variables (optimal_portfolio, dividends) that are not implemented or defined in the current class structure.
# It is commented out to prevent further errors and provide a runnable example for the implemented features.

# # Sin restricciones (0% - 100%)
# optimizer.optimize_with_constraints('sharpe', min_weight=0, max_weight=1)

# # Long only: mínimo 5% por activo
# optimizer.optimize_with_constraints('sharpe', min_weight=0.05, max_weight=1)

# # Máximo 40% por activo
# optimizer.optimize_with_constraints('sharpe', min_weight=0, max_weight=0.40)

# # Custom: 2% mínimo, 30% máximo
# optimizer.optimize_with_constraints('sharpe', min_weight=0.02, max_weight=0.30)


# # Descargar datos CON dividendos
# fetcher = DataFetcher()
# prices, dividends = fetcher.fetch_data(
#     ['AAPL', 'MSFT', 'KO', 'JNJ'],  # Empresas con buenos dividendos
#     start_date='2022-01-01',
#     include_dividends=True  # ⭐ Incluye dividendos
# )
# # Los dividendos se suman automáticamente a los retornos
# optimizer = AdvancedMarkowitzOptimizer(prices, dividends)


# # Backtest con rebalanceo mensual
# backtest = optimizer.backtest_portfolio(
#     weights=optimal_portfolio['weights'],
#     rebalance_freq='monthly',  # daily, weekly, monthly, quarterly
#     initial_capital=10000
# )

# # Resultados
# print(f"Valor Final: ${backtest['final_value']:,.0f}")
# print(f"Retorno Total: {backtest['total_return']*100:.2f}%")
# print(f"Sharpe Ratio: {backtest['sharpe_ratio']:.4f}")
# print(f"Drawdown Máximo: {backtest['max_drawdown']*100:.2f}%")



# # Comparar con S&P 500
# comparison = optimizer.compare_with_benchmark(
#     weights=optimal_portfolio['weights'],
#     benchmark_ticker='SPY'
# )

# # Resultados
# print(f"Portafolio Return: {comparison['portfolio']['return']*100:.2f}%")
# print(f"SPY Return: {comparison['benchmark']['return']*100:.2f}%")
# print(f"Outperformance: {comparison['outperformance']['return']*100:.2f}%")
