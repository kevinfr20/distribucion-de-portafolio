import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
from scipy.stats import norm
import yfinance as yf
from datetime import datetime, timedelta
import warnings
from matplotlib.backends.backend_pdf import PdfPages

warnings.filterwarnings('ignore')
sns.set_style("darkgrid")

# ==================== DATA FETCHER (Unificado) ====================
class DataFetcher:
    """Descarga datos históricos de Yahoo Finance"""

    @staticmethod
    def fetch_data(tickers, start_date=None, end_date=None, include_dividends=False):
        """
        Descarga precios históricos ajustados o precios de cierre.

        Parameters:
        -----------
        tickers : list
            Lista de tickers (ej: ['AAPL', 'MSFT', 'GOOGL'])
        start_date : str
            Fecha inicio (YYYY-MM-DD)
        end_date : str
            Fecha fin (YYYY-MM-DD)
        include_dividends : bool
            Si es True, devuelve también los dividendos (solo para AdvancedMarkowitzOptimizer)

        Returns:
        --------
        pd.DataFrame or tuple : Precios ajustados o (Precios de Cierre, Dividendos) si include_dividends es True
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        print(f"📥 Descargando datos para {tickers} desde {start_date} a {end_date}...")
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)

        if data.empty:
            print(f"❌ Error: No se pudieron descargar datos para {tickers} desde {start_date} hasta {end_date}. Por favor, revise los tickers o el rango de fechas. Retornando DataFrame vacío.")
            if include_dividends:
                return pd.DataFrame(), pd.DataFrame()
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            adj_close_data = None
            close_data = None
            try:
                adj_close_data = data['Adj Close']
            except KeyError:
                pass

            try:
                close_data = data['Close']
            except KeyError:
                pass

            if include_dividends:
                dividends = data['Dividends'] if 'Dividends' in data.columns.get_level_values(0) else pd.DataFrame()
                if close_data is None:
                    print("⚠️ No se encontró la columna 'Close'. Usando 'Adj Close' para cálculo de retornos con dividendos.")
                    if adj_close_data is None:
                         print(f"❌ Error: Ni 'Adj Close' ni 'Close' se encontraron en los datos MultiIndex para {tickers}. Retornando DataFrame vacío.")
                         return pd.DataFrame(), pd.DataFrame()
                    return adj_close_data, dividends
                return close_data, dividends # Para Markowitz con dividendos, usar Close
            else: # When include_dividends is False
                if adj_close_data is not None:
                    return adj_close_data
                elif close_data is not None: # Fallback to 'Close' if 'Adj Close' not found
                    print(f"⚠️ La columna 'Adj Close' no se encontró para {tickers}. Usando 'Close' en su lugar.")
                    return close_data
                else:
                    print(f"❌ Error: Ni 'Adj Close' ni 'Close' se encontraron en los datos MultiIndex para {tickers}. Columnas de primer nivel disponibles: {data.columns.get_level_values(0).unique().tolist()}. Retornando DataFrame vacío.")
                    return pd.DataFrame()
        else:
            if include_dividends:
                dividends = data['Dividends'] if 'Dividends' in data.columns else pd.DataFrame()
                if 'Close' not in data.columns:
                    print("⚠️ No se encontró la columna 'Close'. Usando 'Adj Close' para cálculo de retornos con dividendos.")
                    return data['Adj Close'], dividends
                return data['Close'], dividends
            else:
                if 'Adj Close' not in data.columns:
                    print(f"❌ Error: La columna 'Adj Close' no se encontró en los datos descargados para {tickers}. Retornando DataFrame vacío.")
                    return pd.DataFrame()
                return data['Adj Close']


# ==================== GESTOR DE PORTAFOLIOS UNIFICADO ====================
class UnifiedPortfolioManager:
    """Sistema integrado para análisis de riesgo y optimización de portafolios.

    Combina las funcionalidades de PortfolioRiskManager y AdvancedMarkowitzOptimizer.
    """

    def __init__(self, prices, weights=None, dividends=None):
        """
        Inicializa el gestor de portafolios unificado.

        Parameters:
        -----------
        prices : pd.DataFrame
            DataFrame de precios históricos de los activos.
            Las columnas son los tickers y el índice son las fechas.
        weights : list, optional
            Lista de pesos para cada activo en el portafolio.
            Si no se proporciona, se asumen pesos iguales.
        dividends : pd.DataFrame, optional
            DataFrame de dividendos históricos. Si se proporciona, los retornos
            se ajustarán para incluir dividendos.
        """
        if not isinstance(prices, pd.DataFrame) or prices.empty:
            raise ValueError("prices debe ser un DataFrame de pandas no vacío.")

        self.prices = prices
        self.returns = prices.pct_change().dropna()

        # Ajustar retornos con dividendos si se proporcionan
        if dividends is not None and not dividends.empty:
            common_index = self.returns.index.intersection(dividends.index)
            if not common_index.empty:
                daily_dividends = dividends.reindex(self.prices.index).fillna(0)
                price_shift = self.prices.shift(1)
                dividend_returns = (daily_dividends / price_shift).dropna()
                aligned_dividend_returns = dividend_returns.reindex_like(self.returns).fillna(0)
                self.returns = self.returns + aligned_dividend_returns
                print("✅ Retornos ajustados para incluir dividendos.")
            else:
                print("⚠️ No se encontraron fechas comunes entre precios y dividendos. Los dividendos no se aplicarán.")

        self.num_assets = len(prices.columns)
        self.asset_names = prices.columns.tolist()

        if weights is None:
            self.weights = np.array([1/self.num_assets] * self.num_assets)
        else:
            if len(weights) != self.num_assets:
                raise ValueError("El número de pesos debe coincidir con el número de activos.")
            self.weights = np.array(weights)
            self.weights = self.weights / np.sum(self.weights) # Normalizar pesos

        self.mean_returns = self.returns.mean()
        self.cov_matrix = self.returns.cov()

        # Propiedades calculadas inicialmente
        self.portfolio_return = self.calculate_expected_return()
        self.portfolio_volatility = self.calculate_volatility()

    def _portfolio_performance(self, weights, risk_free_rate=0.01, use_current_mean_cov=True):
        """Calcula el retorno, volatilidad y Sharpe ratio del portafolio.
        Puede usar los mean_returns y cov_matrix precalculados o calcularlos en el momento.
        """
        weights = np.array(weights)
        if use_current_mean_cov:
            returns = np.sum(self.mean_returns * weights) * 252  # Anualizado
            std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix * 252, weights)))  # Anualizado
        else:
            # Fallback a calculos basados en el dataFrame de retornos, como en PortfolioRiskManager original
            returns = np.sum(self.returns.mean() * weights) * 252 # Anualizar
            std = np.sqrt(np.dot(weights.T, np.dot(self.returns.cov() * 252, weights))) # Anualizar

        sharpe = (returns - risk_free_rate) / std if std != 0 else 0
        return returns, std, sharpe

    def calculate_expected_return(self):
        """Calcula el retorno esperado anualizado del portafolio con los pesos actuales."""
        return np.sum(self.mean_returns * self.weights) * 252

    def calculate_volatility(self):
        """Calcula la volatilidad anualizada del portafolio con los pesos actuales."""
        return np.sqrt(np.dot(self.weights.T, np.dot(self.cov_matrix * 252, self.weights)))

    def calculate_sharpe_ratio(self, risk_free_rate=0.01):
        """Calcula el Ratio de Sharpe del portafolio con los pesos actuales."""
        ret = self.calculate_expected_return()
        vol = self.calculate_volatility()
        return (ret - risk_free_rate) / vol if vol != 0 else 0

    def maximum_drawdown(self):
        """Calcula el Máximo Drawdown (MDD) del portafolio."""
        cumulative_returns = (1 + self.returns @ self.weights).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - peak) / peak
        return drawdown.min()

    def calculate_var(self, confidence_level=0.95):
        """Calcula el VaR (Value at Risk) utilizando el método histórico."""
        portfolio_returns = (self.returns * self.weights).sum(axis=1)
        if portfolio_returns.empty:
            return 0
        return -np.percentile(portfolio_returns, (1 - confidence_level) * 100)

    def calculate_cvar(self, confidence_level=0.95):
        """Calcula el CVaR (Conditional Value at Risk) o Expected Shortfall."""
        portfolio_returns = (self.returns * self.weights).sum(axis=1)
        if portfolio_returns.empty:
            return 0
        var = self.calculate_var(confidence_level)
        cvar_returns = portfolio_returns[portfolio_returns < -var]
        return -cvar_returns.mean() if not cvar_returns.empty else 0

    def optimize_portfolio(self, criterion='sharpe', risk_free_rate=0.01, target_return=None, target_volatility=None, bounds=None, update_self_weights=True):
        """Optimiza los pesos del portafolio.

        Parameters:
        -----------
        criterion : str
            Criterio de optimización ('sharpe', 'volatility', 'return', 'target_return', 'target_volatility').
        risk_free_rate : float
            Tasa libre de riesgo.
        target_return : float, optional
            Retorno objetivo para minimizar la volatilidad. Usado con 'target_return' criterion.
        target_volatility : float, optional
            Volatilidad objetivo para maximizar el retorno. Usado con 'target_volatility' criterion.
        bounds : tuple, optional
            Tuplas (min_weight, max_weight) para cada activo.
        update_self_weights : bool
            Si es True, los pesos óptimos encontrados se aplican a la instancia del manager.

        Returns:
        --------
        dict : Pesos óptimos y métricas de rendimiento.
        """
        num_assets = self.num_assets
        initial_weights = np.array([1/num_assets] * num_assets)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        if bounds is None:
            bounds = tuple((0, 1) for _ in range(num_assets))

        if criterion == 'sharpe':
            fun = lambda weights: -self._portfolio_performance(weights, risk_free_rate)[2]
        elif criterion == 'volatility':
            fun = lambda weights: self._portfolio_performance(weights)[1]
        elif criterion == 'return':
            fun = lambda weights: -self._portfolio_performance(weights)[0]
        elif criterion == 'target_return' and target_return is not None:
            fun = lambda weights: self._portfolio_performance(weights)[1]
            constraints = constraints + ({'type': 'eq', 'fun': lambda x: self._portfolio_performance(x)[0] - target_return},)
        elif criterion == 'target_volatility' and target_volatility is not None:
            fun = lambda weights: -self._portfolio_performance(weights)[0]
            constraints = constraints + ({'type': 'eq', 'fun': lambda x: self._portfolio_performance(x)[1] - target_volatility},)
        else:
            raise ValueError("Criterio de optimización no soportado o falta target_return/target_volatility.")

        result = minimize(fun, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

        if result.success:
            optimal_weights = result.x
            if update_self_weights:
                self.weights = optimal_weights # Actualizar pesos del gestor
                self.portfolio_return, self.portfolio_volatility, _ = self._portfolio_performance(optimal_weights, risk_free_rate)

            opt_returns, opt_volatility, opt_sharpe = self._portfolio_performance(optimal_weights, risk_free_rate)
            return {
                'weights': dict(zip(self.asset_names, optimal_weights)),
                'expected_return': opt_returns,
                'volatility': opt_volatility,
                'sharpe_ratio': opt_sharpe
            }
        else:
            raise RuntimeError("Optimización de portafolio fallida: " + result.message)

    def optimize_with_constraints(self, criterion='sharpe', risk_free_rate=0.01, min_weight=0, max_weight=1, update_self_weights=True):
        """Optimiza los pesos con restricciones mínimas y máximas por activo."""
        bounds = tuple((min_weight, max_weight) for _ in range(self.num_assets))
        return self.optimize_portfolio(criterion=criterion, risk_free_rate=risk_free_rate, bounds=bounds, update_self_weights=update_self_weights)

    def stress_test(self, scenarios=None):
        """Realiza un stress test al portafolio bajo diferentes escenarios."""
        if scenarios is None:
            scenarios = {
                'Crisis Financiera': {'factor_return': 0.5, 'factor_volatility': 1.5},
                'Recesión': {'factor_return': 0.7, 'factor_volatility': 1.2},
                'Boom Económico': {'factor_return': 1.2, 'factor_volatility': 0.8}
            }

        results = {}
        original_weights = self.weights
        original_returns_mean = self.mean_returns
        original_cov = self.cov_matrix

        for name, params in scenarios.items():
            scenario_returns = original_returns_mean * params['factor_return']
            scenario_cov = original_cov * params['factor_volatility']

            scenario_portfolio_return = np.sum(scenario_returns * original_weights) * 252
            scenario_portfolio_volatility = np.sqrt(np.dot(original_weights.T, np.dot(scenario_cov * 252, original_weights)))

            results[name] = {
                'expected_return': scenario_portfolio_return,
                'volatility': scenario_portfolio_volatility,
                'sharpe_ratio': (scenario_portfolio_return - 0.01) / scenario_portfolio_volatility if scenario_portfolio_volatility != 0 else 0
            }

        return results

    def monte_carlo_simulation(self, n_simulations=10000, n_days=252, initial_capital=10000):
        """Simulación de Monte Carlo para proyectar el valor del portafolio."""
        portfolio_returns = (self.returns @ self.weights).dropna()
        port_mu = portfolio_returns.mean()
        port_sigma = portfolio_returns.std()

        simulated_prices = np.zeros((n_days, n_simulations))
        simulated_prices[0] = initial_capital

        for s in range(n_simulations):
            daily_returns = np.random.normal(port_mu, port_sigma, n_days - 1)
            simulated_prices[1:, s] = initial_capital * (1 + daily_returns).cumprod()

        final_values = simulated_prices[-1, :]

        return {
            'mean_final': np.mean(final_values),
            'median_final': np.median(final_values),
            'std_final': np.std(final_values),
            'percentile_5': np.percentile(final_values, 5),
            'percentile_95': np.percentile(final_values, 95),
            'simulated_values': simulated_prices
        }

    def backtest_portfolio(self, weights, rebalance_freq='monthly', initial_capital=10000):
        """Realiza un backtest del portafolio con rebalanceo.

        Parameters:
        -----------
        weights : dict
            Diccionario de pesos de los activos (ticker: weight).
        rebalance_freq : str
            Frecuencia de rebalanceo ('daily', 'weekly', 'monthly', 'quarterly', 'yearly').
        initial_capital : float
            Capital inicial del portafolio.

        Returns:
        --------
        dict : Métricas de rendimiento del backtest.
        """
        portfolio_df = pd.DataFrame(index=self.prices.index)
        portfolio_df['Market_Value'] = 0.0

        weights_series = pd.Series(weights)
        weights_series = weights_series[self.asset_names].fillna(0)
        weights_series = weights_series / weights_series.sum() if weights_series.sum() != 0 else pd.Series(1/self.num_assets, index=self.asset_names)

        current_capital = initial_capital
        holdings = pd.Series(0.0, index=self.asset_names) # Número de acciones de cada activo
        last_rebalance_date = None

        rebalance_delta_mapping = {
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': timedelta(days=30), # Aproximado
            'quarterly': timedelta(days=90), # Aproximado
            'yearly': timedelta(days=365) # Aproximado
        }
        rebalance_delta = rebalance_delta_mapping.get(rebalance_freq)
        if rebalance_delta is None:
            raise ValueError("Frecuencia de rebalanceo no soportada.")

        for i, date in enumerate(self.prices.index):
            current_prices = self.prices.loc[date]

            # Solo proceder si tenemos precios válidos para la fecha actual
            if current_prices.isnull().all():
                portfolio_df.loc[date, 'Market_Value'] = portfolio_df.iloc[i-1]['Market_Value'] if i > 0 else initial_capital
                continue

            # Calcular el valor actual del portafolio basado en las tenencias anteriores
            if i > 0:
                current_market_value = (holdings * current_prices).sum()
            else:
                current_market_value = initial_capital # Primera iteracion, usar capital inicial

            # La primera vez o si ha pasado suficiente tiempo para rebalancear
            if last_rebalance_date is None or (date - last_rebalance_date >= rebalance_delta):
                # Rebalancear
                if current_market_value > 0: # Si hay valor en el portafolio, rebalancear
                    target_allocations = current_market_value * weights_series
                    # Evitar division por cero para activos con precio 0, o que no existen
                    holdings = target_allocations / current_prices.replace(0, np.nan).fillna(method='ffill')
                    holdings = holdings.fillna(0) # Si sigue habiendo NaN (ej. activo nuevo sin precio)
                    current_capital = current_market_value
                else: # Si es la primera fecha, usar el capital inicial (esto ya se maneja arriba)
                    # Si current_market_value es 0 por alguna razón, se re-inicializa
                    target_allocations = initial_capital * weights_series
                    holdings = target_allocations / current_prices.replace(0, np.nan).fillna(method='ffill')
                    holdings = holdings.fillna(0)
                    current_capital = initial_capital

                last_rebalance_date = date

            # Actualizar el valor de mercado diario
            portfolio_df.loc[date, 'Market_Value'] = (holdings * current_prices).sum()

        # Calcular métricas
        returns_history = portfolio_df['Market_Value'].pct_change().dropna()
        if returns_history.empty:
            return {"error": "No hay suficientes datos para calcular métricas de backtest."}

        total_return = (portfolio_df['Market_Value'].iloc[-1] / initial_capital) - 1
        annualized_return = (1 + total_return)**(252/len(portfolio_df)) - 1 if len(portfolio_df) > 0 else 0
        annualized_volatility = returns_history.std() * np.sqrt(252) if len(returns_history) > 0 else 0
        sharpe_ratio = (annualized_return - 0.01) / annualized_volatility if annualized_volatility > 0 else 0

        rolling_max = portfolio_df['Market_Value'].cummax()
        daily_drawdown = portfolio_df['Market_Value'] / rolling_max - 1.0
        max_drawdown = daily_drawdown.min()

        return {
            'final_value': portfolio_df['Market_Value'].iloc[-1],
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'portfolio_value_history': portfolio_df['Market_Value']
        }

    def compare_with_benchmark(self, weights, benchmark_ticker='SPY', initial_capital=10000, rebalance_freq='monthly'):
        """Compara el rendimiento del portafolio con un benchmark (ej. S&P 500)."""
        # Backtest del portafolio
        portfolio_backtest = self.backtest_portfolio(weights, rebalance_freq, initial_capital)
        portfolio_returns_history = portfolio_backtest['portfolio_value_history'].pct_change().dropna()

        # Descargar datos del benchmark
        benchmark_prices = DataFetcher.fetch_data([benchmark_ticker],
                                                  start_date=self.prices.index.min().strftime('%Y-%m-%d'),
                                                  end_date=self.prices.index.max().strftime('%Y-%m-%d'))
        if benchmark_prices.empty or benchmark_ticker not in benchmark_prices.columns:
            print(f"❌ No se pudieron descargar datos para el benchmark {benchmark_ticker}.")
            return None

        benchmark_returns_history = benchmark_prices[benchmark_ticker].pct_change().dropna()

        # Alinear los índices para la comparación
        common_dates = portfolio_returns_history.index.intersection(benchmark_returns_history.index)
        if common_dates.empty:
            print("❌ No hay fechas comunes entre el portafolio y el benchmark para la comparación.")
            return None

        portfolio_returns_aligned = portfolio_returns_history.loc[common_dates]
        benchmark_returns_aligned = benchmark_returns_history.loc[common_dates]

        # Calcular rendimientos acumulados para el mismo período
        portfolio_cumulative_return = (1 + portfolio_returns_aligned).prod() - 1
        benchmark_cumulative_return = (1 + benchmark_returns_aligned).prod() - 1

        return {
            'portfolio': {
                'return': portfolio_cumulative_return,
                'final_value': initial_capital * (1 + portfolio_cumulative_return)
            },
            'benchmark': {
                'ticker': benchmark_ticker,
                'return': benchmark_cumulative_return,
                'final_value': initial_capital * (1 + benchmark_cumulative_return)
            },
            'outperformance': {
                'return': portfolio_cumulative_return - benchmark_cumulative_return
            }
        }

    def plot_efficient_frontier(self, risk_free_rate=0.01, num_portfolios=10000):
        """Genera la frontera eficiente y muestra los portafolios óptimos."""
        results = np.zeros((3, num_portfolios))
        all_weights = np.zeros((num_portfolios, self.num_assets))

        for i in range(num_portfolios):
            weights = np.random.random(self.num_assets)
            weights /= np.sum(weights)
            all_weights[i, :] = weights

            p_returns, p_std, p_sharpe = self._portfolio_performance(weights, risk_free_rate)
            results[0, i] = p_std
            results[1, i] = p_returns
            results[2, i] = p_sharpe

        plt.figure(figsize=(12, 8))
        plt.scatter(results[0,:], results[1,:], c=results[2,:], cmap='viridis', marker='o', s=10, alpha=0.5)
        plt.colorbar(label='Sharpe Ratio')
        plt.xlabel('Volatilidad Anualizada')
        plt.ylabel('Retorno Anualizado')
        plt.title('Frontera Eficiente')

        # Portafolio de Máximo Sharpe
        try:
            max_sharpe_portfolio = self.optimize_portfolio('sharpe', risk_free_rate, update_self_weights=False)
            plt.scatter(max_sharpe_portfolio['volatility'], max_sharpe_portfolio['expected_return'], marker='*', color='red', s=500, label='Máximo Sharpe')
        except Exception as e:
            print(f"⚠️ No se pudo calcular el portafolio de Máximo Sharpe para la frontera eficiente: {e}")
            max_sharpe_portfolio = {'weights': {}, 'expected_return': 0, 'volatility': 0, 'sharpe_ratio': 0}

        # Portafolio de Mínima Volatilidad
        try:
            min_vol_portfolio = self.optimize_portfolio('volatility', update_self_weights=False)
            plt.scatter(min_vol_portfolio['volatility'], min_vol_portfolio['expected_return'], marker='X', color='blue', s=500, label='Mínima Volatilidad')
        except Exception as e:
            print(f"⚠️ No se pudo calcular el portafolio de Mínima Volatilidad para la frontera eficiente: {e}")
            min_vol_portfolio = {'weights': {}, 'expected_return': 0, 'volatility': 0, 'sharpe_ratio': 0}

        plt.legend(labelspacing=0.8)
        plt.grid(True)
        plt.show()

        return {
            'max_sharpe_portfolio': max_sharpe_portfolio,
            'min_vol_portfolio': min_vol_portfolio
        }

    def plot_portfolio_performance(self):
        """Genera gráficos de rendimiento del portafolio."""
        plt.figure(figsize=(12, 6))
        cumulative_returns = (1 + self.returns @ self.weights).cumprod()
        cumulative_returns.plot(title='Rendimiento Acumulado del Portafolio')
        plt.xlabel('Fecha')
        plt.ylabel('Retorno Acumulado')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        plt.figure(figsize=(12, 6))
        sns.heatmap(self.returns.corr(), annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Matriz de Correlación de Activos')
        plt.tight_layout()
        plt.show()

    def export_to_pdf(self, filename='portfolio_report.pdf', risk_free_rate=0.01, n_simulations_mc=10000, initial_capital_mc=10000, initial_capital_bt=10000):
        """Genera un reporte PDF completo del análisis de portafolio."""
        with PdfPages(filename) as pdf:
            # Página de Resumen General
            fig1, ax1 = plt.subplots(figsize=(10, 2))
            ax1.axis('off')
            summary = self.get_portfolio_summary(risk_free_rate)
            summary_text = f"""Análisis Completo del Portafolio

Fecha del Reporte: {summary['timestamp']}
Activos: {', '.join(summary['assets'])}
Pesos: {', '.join([f'{k}: {v:.2%}' for k,v in summary['weights'].items()])}

Retorno Esperado (Anualizado): {summary['expected_return']*100:.2f}%
Volatilidad (Anualizada): {summary['volatility']*100:.2f}%
Ratio de Sharpe: {summary['sharpe_ratio']:.4f}
Máximo Drawdown: {summary['max_drawdown']*100:.2f}%
VaR 95% (Diario): {summary['var_95']*100:.2f}%
CVaR 95% (Diario): {summary['cvar_95']*100:.2f}%"""

            ax1.text(0.05, 0.9, summary_text, transform=ax1.transAxes, fontsize=12, verticalalignment='top')
            pdf.savefig(fig1, bbox_inches='tight')
            plt.close(fig1)

            # Gráfico de Rendimiento Acumulado
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            cumulative_returns = (1 + self.returns @ self.weights).cumprod()
            cumulative_returns.plot(ax=ax2, title='Rendimiento Acumulado del Portafolio')
            ax2.set_xlabel('Fecha')
            ax2.set_ylabel('Retorno Acumulado')
            ax2.grid(True)
            pdf.savefig(fig2, bbox_inches='tight')
            plt.close(fig2)

            # Gráfico de Matriz de Correlación
            fig3, ax3 = plt.subplots(figsize=(10, 8))
            sns.heatmap(self.returns.corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax3)
            ax3.set_title('Matriz de Correlación de Activos')
            pdf.savefig(fig3, bbox_inches='tight')
            plt.close(fig3)

            # Stress Test
            stress_results = self.stress_test()
            fig4, ax4 = plt.subplots(figsize=(10, 6))
            scenario_names = list(stress_results.keys())
            scenario_returns = [r['expected_return']*100 for r in stress_results.values()]
            scenario_volatilities = [v['volatility']*100 for v in stress_results.values()]

            width = 0.35
            x = np.arange(len(scenario_names))
            rects1 = ax4.bar(x - width/2, scenario_returns, width, label='Retorno Esperado (%)')
            rects2 = ax4.bar(x + width/2, scenario_volatilities, width, label='Volatilidad (%)')

            ax4.set_ylabel('Porcentaje')
            ax4.set_title('Stress Test del Portafolio: Retorno y Volatilidad por Escenario')
            ax4.set_xticks(x)
            ax4.set_xticklabels(scenario_names)
            ax4.legend()
            ax4.grid(axis='y')
            pdf.savefig(fig4, bbox_inches='tight')
            plt.close(fig4)

            # Monte Carlo Simulation
            mc_results = self.monte_carlo_simulation(n_simulations=n_simulations_mc, initial_capital=initial_capital_mc)
            fig5, ax5 = plt.subplots(figsize=(10, 6))
            ax5.hist(mc_results['simulated_values'][-1, :], bins=50, alpha=0.7, color='blue')
            ax5.axvline(mc_results['mean_final'], color='red', linestyle='dashed', linewidth=1, label=f'Media: ${mc_results['mean_final']:,.0f}')
            ax5.axvline(mc_results['percentile_5'], color='green', linestyle='dashed', linewidth=1, label=f'VaR 95%: ${mc_results['percentile_5']:,.0f}')
            ax5.set_title('Distribución de Valores Finales (Monte Carlo)')
            ax5.set_xlabel('Valor Final del Portafolio')
            ax5.set_ylabel('Frecuencia')
            ax5.legend()
            pdf.savefig(fig5, bbox_inches='tight')
            plt.close(fig5)

            # Backtesting
            # Usamos los pesos actuales del manager para el backtest por defecto
            current_weights_dict = dict(zip(self.asset_names, self.weights))
            backtest_results = self.backtest_portfolio(weights=current_weights_dict, initial_capital=initial_capital_bt)
            if 'portfolio_value_history' in backtest_results:
                fig6, ax6 = plt.subplots(figsize=(10, 6))
                backtest_results['portfolio_value_history'].plot(ax=ax6, title='Backtesting: Rendimiento Acumulado del Portafolio')
                ax6.set_xlabel('Fecha')
                ax6.set_ylabel('Valor del Portafolio')
                ax6.grid(True)
                pdf.savefig(fig6, bbox_inches='tight')
                plt.close(fig6)
            else:
                print(f"⚠️ No se pudo generar el gráfico de Backtesting: {backtest_results.get('error', 'Error desconocido')}")

            print(f"✅ Reporte PDF '{filename}' generado exitosamente.")

    def get_portfolio_summary(self, risk_free_rate=0.01):
        """Devuelve un diccionario con un resumen del portafolio."""
        return {
            'timestamp': datetime.now().isoformat(),
            'assets': list(self.prices.columns),
            'weights': dict(zip(self.prices.columns, self.weights)),
            'expected_return': self.calculate_expected_return(),
            'volatility': self.calculate_volatility(),
            'sharpe_ratio': self.calculate_sharpe_ratio(risk_free_rate),
            'var_95': self.calculate_var(0.95),
            'cvar_95': self.calculate_cvar(0.95),
            'max_drawdown': self.maximum_drawdown()
        }


# ==================== EJEMPLO DE USO UNIFICADO ====================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 SISTEMA INTEGRADO DE ANÁLISIS Y OPTIMIZACIÓN DE PORTAFOLIOS (UNIFICADO)")
    print("="*80 + "\n")

    # Configuración de los activos y fechas
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    start_date = '2023-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    initial_capital_value = 100000

    # 1. Descargar datos utilizando el DataFetcher unificado
    fetcher = DataFetcher()
    # Para el UnifiedPortfolioManager, usamos Adj Close para el 'prices' principal
    prices = fetcher.fetch_data(tickers, start_date=start_date, end_date=end_date)

    if prices.empty:
        print("❌ No se pudieron obtener datos. Terminando ejecución.")
    else:
        print("✅ Datos descargados exitosamente.\n")

        # ==================== Inicialización y Análisis Básico ====================
        print("\n" + "-"*70)
        print("📊 INICIALIZACIÓN Y ANÁLISIS BÁSICO (UnifiedPortfolioManager)")
        print("-"*70 + "\n")

        # Creamos un portafolio con pesos iguales inicialmente
        unified_manager = UnifiedPortfolioManager(prices)
        print("✅ Portafolio inicial creado con pesos iguales.\n")

        # Resumen del portafolio inicial
        summary_initial = unified_manager.get_portfolio_summary()
        print("📋 Resumen del Portafolio Inicial:")
        for k, v in summary_initial.items():
            if k == 'weights':
                print(f"   {k.replace('_', ' ').title()}: {', '.join([f'{asset}: {weight:.2%}' for asset, weight in v.items()])}")
            elif isinstance(v, (float, np.float64)) and k not in ['timestamp', 'assets']:
                print(f"   {k.replace('_', ' ').title()}: {v*100:.2f}%" if 'return' in k or 'volatility' in k or 'drawdown' in k or 'var' in k else f"   {k.replace('_', ' ').title()}: {v:.4f}")
            else:
                print(f"   {k.replace('_', ' ').title()}: {v}")
        print("\n")

        # ==================== Optimización de Portafolio ====================
        print("\n" + "-"*70)
        print("🎯 OPTIMIZACIÓN DE PORTAFOLIO")
        print("-"*70 + "\n")

        # Optimizar el portafolio para maximizar Sharpe
        print("🚀 Buscando el Portafolio de Máximo Sharpe...")
        try:
            optimal_sharpe_portfolio = unified_manager.optimize_portfolio('sharpe', update_self_weights=True)
            print("✅ Portafolio de Máximo Sharpe Encontrado y aplicado al manager.\n")
            summary_optimized_sharpe = unified_manager.get_portfolio_summary()
            print("📋 Resumen del Portafolio Optimizado (Máximo Sharpe):")
            for k, v in summary_optimized_sharpe.items():
                if k == 'weights':
                    print(f"   {k.replace('_', ' ').title()}: {', '.join([f'{asset}: {weight:.2%}' for asset, weight in v.items()])}")
                elif isinstance(v, (float, np.float64)) and k not in ['timestamp', 'assets']:
                    print(f"   {k.replace('_', ' ').title()}: {v*100:.2f}%" if 'return' in k or 'volatility' in k or 'drawdown' in k or 'var' in k else f"   {k.replace('_', ' ').title()}: {v:.4f}")
                else:
                    print(f"   {k.replace('_', ' ').title()}: {v}")
            print("\n")
        except RuntimeError as e:
            print(f"❌ Error al optimizar para Máximo Sharpe: {e}\n")
            optimal_sharpe_portfolio = {'weights': dict(zip(tickers, [1/len(tickers)]*len(tickers))), 'expected_return': 0, 'volatility': 0, 'sharpe_ratio': 0}

        # Optimizar para la Mínima Volatilidad (sin actualizar self.weights)
        print("🐢 Buscando el Portafolio de Mínima Volatilidad (no se aplican los pesos)...")
        try:
            optimal_vol_portfolio = unified_manager.optimize_portfolio('volatility', update_self_weights=False)
            print("   Portafolio de Mínima Volatilidad Encontrado:")
            for asset, weight in optimal_vol_portfolio['weights'].items():
                print(f"      {asset}: {weight*100:.2f}%")
            print(f"   Retorno Esperado: {optimal_vol_portfolio['expected_return']*100:.2f}%")
            print(f"   Volatilidad: {optimal_vol_portfolio['volatility']*100:.2f}%")
            print(f"   Sharpe Ratio: {optimal_vol_portfolio['sharpe_ratio']:.4f}\n")
        except RuntimeError as e:
            print(f"❌ Error al optimizar para Mínima Volatilidad: {e}\n")

        # Plotear la Frontera Eficiente
        print("📊 Generando la Frontera Eficiente...")
        try:
            unified_manager.plot_efficient_frontier()
            print("✅ Frontera Eficiente generada.\n")
        except Exception as e:
            print(f"❌ Error al plotear la Frontera Eficiente: {e}\n")


        # Plotear rendimiento de portafolio
        print("📊 Generando rendimiento del portafolio...")
        try:
            unified_manager.plot_portfolio_performance()
            print("✅ Rendimiento Acumulado del Portafolio.\n")
        except Exception as e:
            print(f"❌ Error al plotear rendimento de portafolio: {e}\n")
        # ==================== Gestión de Riesgos y Backtesting ====================
        print("\n" + "-"*70)
        print("⚠️ GESTIÓN DE RIESGOS Y BACKTESTING")
        print("-"*70 + "\n")

        # Realizar Stress Test
        print("⚠️ Ejecutando Stress Test...")
        stress_results = unified_manager.stress_test()
        print("   Resultados del Stress Test:")
        for scenario, res in stress_results.items():
            print(f"      - {scenario}: Retorno={res['expected_return']*100:.2f}%, Volatilidad={res['volatility']*100:.2f}%")
        print("\n")

        # Realizar Simulación de Monte Carlo
        print("🎲 Ejecutando Simulación de Monte Carlo...")
        mc_results = unified_manager.monte_carlo_simulation(initial_capital=initial_capital_value)
        print(f"   Valor Final Esperado (MC): ${mc_results['mean_final']:,.2f}")
        print(f"   VaR 95% (MC): ${mc_results['percentile_5']:,.2f}\n")

        # Backtesting del portafolio (con rebalanceo, usando los pesos optimizados por sharpe)
        print("📈 Realizando Backtesting (con rebalanceo mensual de los pesos de Máximo Sharpe)...")
        try:
            backtest_results = unified_manager.backtest_portfolio(
                weights=optimal_sharpe_portfolio['weights'],
                rebalance_freq='monthly',
                initial_capital=initial_capital_value
            )
            print(f"   Capital Inicial: ${backtest_results['initial_capital']:,.2f}" if 'initial_capital' in backtest_results else "")
            print(f"   Capital Final: ${backtest_results['final_value']:,.2f}")
            print(f"   Retorno Total: {backtest_results['total_return']*100:.2f}%")
            print(f"   Sharpe Ratio (Backtest): {backtest_results['sharpe_ratio']:.4f}")
            print(f"   Máximo Drawdown (Backtest): {backtest_results['max_drawdown']*100:.2f}%\n")
        except Exception as e:
            print(f"❌ Error durante el backtesting: {e}\n")

        # Comparar con un Benchmark (ej. SPY)
        print("🆚 Comparando el Portafolio Optimizado (Máximo Sharpe) con SPY...")
        try:
            comparison_results = unified_manager.compare_with_benchmark(
                weights=optimal_sharpe_portfolio['weights'],
                benchmark_ticker='SPY',
                initial_capital=initial_capital_value,
                rebalance_freq='monthly'
            )
            if comparison_results:
                print(f"   Retorno del Portafolio Optimizado: {comparison_results['portfolio']['return']*100:.2f}%")
                print(f"   Retorno del Benchmark ({comparison_results['benchmark']['ticker']}): {comparison_results['benchmark']['return']*100:.2f}%")
                print(f"   Outperformance: {comparison_results['outperformance']['return']*100:.2f}%\n")
        except Exception as e:
            print(f"❌ Error al comparar con benchmark: {e}\n")

        # Generar Reporte PDF (descomentar para usar)
        # print("📄 Generando reporte PDF completo...")
        # unified_manager.export_to_pdf('informe_portfolio_unificado.pdf', initial_capital_mc=initial_capital_value, initial_capital_bt=initial_capital_value)
        # print("✅ Reporte PDF generado exitosamente.\n")

    print("\n" + "="*80)
    print("✅ ¡ANÁLISIS Y OPTIMIZACIÓN INTEGRADOS COMPLETADOS!")
    print("="*80 + "\n")
