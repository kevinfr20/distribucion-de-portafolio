import numpy as np
import pandas as pd
from scipy.stats import norm, t
import warnings

warnings.filterwarnings('ignore')


# ==================== MÉTRICAS DE RIESGO AVANZADAS ====================

class RiskMetricsCalculator:
    """Calcula métricas avanzadas de riesgo para portafolios"""
    
    def __init__(self, returns, confidence_level=0.95):
        """
        Inicializa el calculador de métricas de riesgo.
        
        Parameters:
        -----------
        returns : pd.Series o pd.DataFrame
            Retornos históricos (diarios)
        confidence_level : float
            Nivel de confianza para VaR/CVaR (default: 0.95)
        """
        self.returns = returns if isinstance(returns, pd.Series) else returns.mean(axis=1)
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    def calculate_var_historical(self):
        """Calcula VaR usando el método histórico"""
        return -np.percentile(self.returns, self.alpha * 100)
    
    def calculate_var_parametric(self):
        """Calcula VaR usando el método paramétrico (distribución normal)"""
        mu = self.returns.mean()
        sigma = self.returns.std()
        z_score = norm.ppf(self.alpha)
        return -(mu + z_score * sigma)
    
    def calculate_cvar(self):
        """Calcula CVaR (Expected Shortfall)"""
        var_historical = self.calculate_var_historical()
        cvar_returns = self.returns[self.returns <= -var_historical]
        return -cvar_returns.mean() if not cvar_returns.empty else var_historical
    
    def calculate_expected_shortfall(self):
        """Alias para CVaR"""
        return self.calculate_cvar()
    
    def calculate_maximum_drawdown(self):
        """Calcula el máximo drawdown"""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def calculate_calmar_ratio(self, annualized_return):
        """
        Calcula el Ratio de Calmar.
        
        Parameters:
        -----------
        annualized_return : float
            Retorno anualizado
        
        Returns:
        --------
        float : Calmar Ratio
        """
        max_dd = self.calculate_maximum_drawdown()
        return annualized_return / abs(max_dd) if max_dd != 0 else 0
    
    def calculate_sortino_ratio(self, target_return=0, risk_free_rate=0.01):
        """
        Calcula el Ratio de Sortino.
        
        Parameters:
        -----------
        target_return : float
            Retorno objetivo (default: 0)
        risk_free_rate : float
            Tasa libre de riesgo
        
        Returns:
        --------
        float : Sortino Ratio
        """
        excess_return = self.returns - target_return
        downside_returns = excess_return[excess_return < 0]
        downside_std = downside_returns.std()
        
        annualized_return = self.returns.mean() * 252
        return (annualized_return - risk_free_rate) / (downside_std * np.sqrt(252)) if downside_std != 0 else 0
    
    def calculate_omega_ratio(self, threshold=0):
        """
        Calcula el Ratio Omega.
        
        Parameters:
        -----------
        threshold : float
            Retorno de referencia (default: 0)
        
        Returns:
        --------
        float : Omega Ratio
        """
        excess_returns = self.returns - threshold
        gains = excess_returns[excess_returns > 0].sum()
        losses = -excess_returns[excess_returns < 0].sum()
        
        return gains / losses if losses != 0 else 0
    
    def calculate_information_ratio(self, benchmark_returns, annualized=True):
        """
        Calcula el Ratio de Información.
        
        Parameters:
        -----------
        benchmark_returns : pd.Series
            Retornos del benchmark
        annualized : bool
            Si debe anualizarse
        
        Returns:
        --------
        float : Information Ratio
        """
        active_returns = self.returns - benchmark_returns
        active_return = active_returns.mean()
        tracking_error = active_returns.std()
        
        if annualized:
            active_return *= 252
            tracking_error *= np.sqrt(252)
        
        return active_return / tracking_error if tracking_error != 0 else 0
    
    def calculate_skewness(self):
        """Calcula la asimetría (skewness) de los retornos"""
        return self.returns.skew()
    
    def calculate_kurtosis(self):
        """Calcula la curtosis (kurtosis) de los retornos"""
        return self.returns.kurtosis()
    
    def calculate_tail_ratio(self):
        """
        Calcula el ratio de colas.
        Mide la relación entre pérdidas extremas y ganancias extremas.
        """
        percentile_5 = np.percentile(self.returns, 5)
        percentile_95 = np.percentile(self.returns, 95)
        
        losses = self.returns[self.returns <= percentile_5]
        gains = self.returns[self.returns >= percentile_95]
        
        avg_loss = abs(losses.mean())
        avg_gain = gains.mean()
        
        return avg_loss / avg_gain if avg_gain != 0 else 0
    
    def calculate_var_conditional_normal(self):
        """Calcula VaR condicional usando distribución normal multivariada"""
        mu = self.returns.mean()
        sigma = self.returns.std()
        z_score = norm.ppf(self.alpha)
        
        conditional_expectation = mu + sigma * (norm.pdf(z_score) / self.alpha)
        return -conditional_expectation
    
    def calculate_rolling_var(self, window=30):
        """
        Calcula VaR móvil.
        
        Parameters:
        -----------
        window : int
            Tamaño de la ventana móvil
        
        Returns:
        --------
        pd.Series : VaR móvil
        """
        return self.returns.rolling(window).apply(
            lambda x: -np.percentile(x, self.alpha * 100)
        )
    
    def calculate_rolling_volatility(self, window=30):
        """
        Calcula volatilidad móvil.
        
        Parameters:
        -----------
        window : int
            Tamaño de la ventana móvil
        
        Returns:
        --------
        pd.Series : Volatilidad móvil
        """
        return self.returns.rolling(window).std()
    
    def get_risk_summary(self, annualized_return, annualized_volatility):
        """
        Devuelve un resumen completo de métricas de riesgo.
        
        Parameters:
        -----------
        annualized_return : float
            Retorno anualizado
        annualized_volatility : float
            Volatilidad anualizada
        
        Returns:
        --------
        dict : Diccionario con todas las métricas de riesgo
        """
        return {
            'var_historical': self.calculate_var_historical(),
            'var_parametric': self.calculate_var_parametric(),
            'cvar': self.calculate_cvar(),
            'max_drawdown': self.calculate_maximum_drawdown(),
            'calmar_ratio': self.calculate_calmar_ratio(annualized_return),
            'sortino_ratio': self.calculate_sortino_ratio(),
            'omega_ratio': self.calculate_omega_ratio(),
            'skewness': self.calculate_skewness(),
            'kurtosis': self.calculate_kurtosis(),
            'tail_ratio': self.calculate_tail_ratio()
        }


class VolatilityPredictor:
    """Predice volatilidad futura usando GARCH"""
    
    def __init__(self, returns):
        """
        Inicializa el predictor de volatilidad.
        
        Parameters:
        -----------
        returns : pd.Series
            Retornos históricos
        """
        self.returns = returns
        self.historical_vol = returns.std()
    
    def calculate_ewma_volatility(self, span=30):
        """
        Calcula volatilidad usando EWMA (Exponentially Weighted Moving Average).
        
        Parameters:
        -----------
        span : int
            Período de decaimiento exponencial
        
        Returns:
        --------
        pd.Series : Volatilidad EWMA
        """
        return self.returns.ewm(span=span).std()
    
    def simple_garch_forecast(self, omega=0.0001, alpha=0.05, beta=0.94, horizon=30):
        """
        Predicción simple de volatilidad usando GARCH(1,1).
        
        Parameters:
        -----------
        omega : float
            Componente de volatilidad a largo plazo
        alpha : float
            Ponderación de shocks recientes
        beta : float
            Ponderación de volatilidad anterior
        horizon : int
            Horizonte de predicción en días
        
        Returns:
        --------
        float : Volatilidad predicha
        """
        long_term_var = self.historical_vol ** 2
        recent_return_shock = self.returns.iloc[-1] ** 2
        recent_variance = self.returns.iloc[-30:].var()
        
        forecast_variance = omega
        forecast_variance += alpha * recent_return_shock
        forecast_variance += beta * recent_variance
        
        for _ in range(horizon - 1):
            forecast_variance = omega + (alpha + beta) * forecast_variance
        
        return np.sqrt(forecast_variance)


class CorrelationAnalyzer:
    """Analiza cambios en correlaciones"""
    
    def __init__(self, returns):
        """
        Inicializa el analizador de correlaciones.
        
        Parameters:
        -----------
        returns : pd.DataFrame
            Retornos de múltiples activos
        """
        self.returns = returns
    
    def rolling_correlation(self, window=60):
        """
        Calcula correlación móvil entre activos.
        
        Parameters:
        -----------
        window : int
            Tamaño de la ventana móvil
        
        Returns:
        --------
        pd.DataFrame : Matriz de correlación móvil
        """
        return self.returns.rolling(window).corr()
    
    def detect_correlation_breakdown(self, window=60, threshold=0.2):
        """
        Detecta cambios significativos en correlaciones.
        
        Parameters:
        -----------
        window : int
            Tamaño de la ventana móvil
        threshold : float
            Cambio mínimo para considerar significativo
        
        Returns:
        --------
        dict : Períodos donde hubo cambios significativos
        """
        rolling_corr = self.rolling_correlation(window)
        static_corr = self.returns.corr()
        
        changes = {}
        for col in rolling_corr.columns.get_level_values(0).unique():
            max_change = abs(rolling_corr[col] - static_corr.loc[col]).max()
            if max_change > threshold:
                changes[col] = max_change
        
        return changes
    
    def get_correlation_regime(self):
        """Identifica el régimen actual de correlaciones (alto/bajo)"""
        static_corr = self.returns.corr()
        avg_corr = static_corr.values[np.triu_indices_from(static_corr.values, k=1)].mean()
        
        return {
            'average_correlation': avg_corr,
            'regime': 'High Correlation' if avg_corr > 0.5 else 'Low Correlation'
        }
