"""
Módulo de Métricas Avanzadas de Riesgo para Portafolios
========================================================

Este módulo proporciona cálculos avanzados de riesgo incluyendo:
- Value at Risk (VaR) - Histórico, Paramétrico, Monte Carlo
- Conditional Value at Risk (CVaR/Expected Shortfall)
- Maximum Drawdown y análisis de drawdown
- Volatilidad predictiva (GARCH)
- Beta y correlación dinámica
- Stress testing avanzado
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import minimize
import warnings

warnings.filterwarnings('ignore')


class AdvancedRiskMetrics:
    """Cálculo de métricas avanzadas de riesgo para portafolios"""
    
    def __init__(self, returns, weights=None):
        """
        Inicializa el calculador de métricas de riesgo
        
        Parameters:
        -----------
        returns : pd.DataFrame o pd.Series
            Retornos históricos del portafolio o activos
        weights : array-like, optional
            Pesos de los activos (si returns es DataFrame)
        """
        self.returns = returns if isinstance(returns, pd.Series) else (returns @ weights if weights is not None else returns.mean(axis=1))
        self.weights = weights
        self.price_data = None
    
    def calculate_var_parametric(self, confidence_level=0.95, periods=252):
        """
        Calcula VaR paramétrico asumiendo distribución normal
        
        Parameters:
        -----------
        confidence_level : float
            Nivel de confianza (ej: 0.95 para 95%)
        periods : int
            Días de proyección
            
        Returns:
        --------
        float : VaR paramétrico (en términos de retorno)
        """
        mean_return = self.returns.mean()
        std_return = self.returns.std()
        z_score = norm.ppf(1 - confidence_level)
        return mean_return * periods + z_score * std_return * np.sqrt(periods)
    
    def calculate_var_historical(self, confidence_level=0.95):
        """
        Calcula VaR histórico usando percentiles
        
        Parameters:
        -----------
        confidence_level : float
            Nivel de confianza
            
        Returns:
        --------
        float : VaR histórico
        """
        return -np.percentile(self.returns, (1 - confidence_level) * 100)
    
    def calculate_cvar(self, confidence_level=0.95):
        """
        Calcula CVaR (Expected Shortfall) - promedio de pérdidas extremas
        
        Parameters:
        -----------
        confidence_level : float
            Nivel de confianza
            
        Returns:
        --------
        float : CVaR (pérdida esperada condicional)
        """
        var_threshold = self.calculate_var_historical(confidence_level)
        extreme_losses = self.returns[self.returns < -var_threshold]
        return -extreme_losses.mean() if len(extreme_losses) > 0 else var_threshold
    
    def calculate_drawdown(self):
        """
        Calcula drawdown para cada punto en el tiempo
        
        Returns:
        --------
        pd.Series : Drawdown diario
        pd.Series : Drawdown acumulado (peak-to-trough)
        """
        cumulative_returns = (1 + self.returns).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - peak) / peak
        
        # Drawdown acumulado (diferente del diario)
        cumulative_dd = drawdown.min()
        
        return drawdown, cumulative_dd
    
    def calculate_max_drawdown(self):
        """
        Calcula el máximo drawdown histórico
        
        Returns:
        --------
        float : Máximo drawdown
        """
        _, max_dd = self.calculate_drawdown()
        return max_dd
    
    def calculate_recovery_time(self):
        """
        Calcula el tiempo promedio de recuperación después de un drawdown
        
        Returns:
        --------
        float : Días promedio de recuperación
        """
        cumulative_returns = (1 + self.returns).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        
        # Identificar períodos de drawdown
        in_drawdown = cumulative_returns < peak
        
        # Contar períodos consecutivos en drawdown
        drawdown_groups = (in_drawdown != in_drawdown.shift()).cumsum()
        drawdown_lengths = drawdown_groups[in_drawdown].value_counts()
        
        return drawdown_lengths.mean() if len(drawdown_lengths) > 0 else 0
    
    def calculate_calmar_ratio(self):
        """
        Calcula el Ratio de Calmar (retorno anualizado / máximo drawdown)
        
        Returns:
        --------
        float : Calmar Ratio
        """
        annual_return = self.returns.mean() * 252
        max_dd = abs(self.calculate_max_drawdown())
        return annual_return / max_dd if max_dd != 0 else 0
    
    def calculate_sortino_ratio(self, target_return=0.0, periods=252, risk_free_rate=0.01):
        """
        Calcula el Ratio de Sortino (solo considera desviación negativa)
        
        Parameters:
        -----------
        target_return : float
            Retorno mínimo aceptable
        periods : int
            Períodos de anualización
        risk_free_rate : float
            Tasa libre de riesgo
            
        Returns:
        --------
        float : Sortino Ratio
        """
        excess_returns = self.returns - target_return
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = np.sqrt(np.mean(downside_returns**2)) * np.sqrt(periods)
        
        annual_return = self.returns.mean() * periods
        return (annual_return - risk_free_rate) / downside_std if downside_std != 0 else 0
    
    def calculate_omega_ratio(self, min_acceptable_return=0.0):
        """
        Calcula el Ratio Omega (probabilidad ponderada de ganancias vs pérdidas)
        
        Parameters:
        -----------
        min_acceptable_return : float
            Retorno mínimo aceptable
            
        Returns:
        --------
        float : Omega Ratio
        """
        excess_returns = self.returns - min_acceptable_return
        gains = excess_returns[excess_returns > 0].sum()
        losses = abs(excess_returns[excess_returns < 0].sum())
        
        return gains / losses if losses != 0 else np.inf
    
    def stress_test_scenarios(self, scenarios_dict=None):
        """
        Realiza stress test con múltiples escenarios personalizados
        
        Parameters:
        -----------
        scenarios_dict : dict
            Diccionario con escenarios y sus parámetros
            
        Returns:
        --------
        dict : Resultados del stress test
        """
        if scenarios_dict is None:
            scenarios_dict = {
                'Crisis Financiera': {'factor_return': 0.5, 'factor_volatility': 2.0},
                'Recesión Moderada': {'factor_return': 0.7, 'factor_volatility': 1.5},
                'Volatilidad Alta': {'factor_return': 1.0, 'factor_volatility': 2.0},
                'Normalidad': {'factor_return': 1.0, 'factor_volatility': 1.0},
                'Boom Económico': {'factor_return': 1.3, 'factor_volatility': 0.8}
            }
        
        results = {}
        original_mean = self.returns.mean()
        original_std = self.returns.std()
        
        for scenario_name, params in scenarios_dict.items():
            stressed_mean = original_mean * params['factor_return']
            stressed_std = original_std * params['factor_volatility']
            
            # Simular retornos bajo estrés
            stressed_returns = np.random.normal(stressed_mean, stressed_std, len(self.returns))
            stressed_series = pd.Series(stressed_returns, index=self.returns.index)
            
            results[scenario_name] = {
                'mean_return': stressed_mean * 252,
                'volatility': stressed_std * np.sqrt(252),
                'var_95': -np.percentile(stressed_returns, 5),
                'cvar_95': -np.percentile(stressed_returns, 1),
                'max_drawdown': self._calculate_drawdown_from_returns(stressed_returns)
            }
        
        return results
    
    @staticmethod
    def _calculate_drawdown_from_returns(returns_array):
        """Calcula drawdown a partir de un array de retornos"""
        cumulative = np.cumprod(1 + returns_array)
        peak = np.maximum.accumulate(cumulative)
        return np.min((cumulative - peak) / peak)
    
    def calculate_rolling_var(self, window=60, confidence_level=0.95):
        """
        Calcula VaR rolling (ventana móvil)
        
        Parameters:
        -----------
        window : int
            Tamaño de la ventana
        confidence_level : float
            Nivel de confianza
            
        Returns:
        --------
        pd.Series : VaR rolling
        """
        return self.returns.rolling(window).apply(
            lambda x: -np.percentile(x, (1 - confidence_level) * 100),
            raw=False
        )
    
    def calculate_rolling_volatility(self, window=60, periods=252):
        """
        Calcula volatilidad rolling anualizada
        
        Parameters:
        -----------
        window : int
            Tamaño de la ventana
        periods : int
            Períodos de anualización
            
        Returns:
        --------
        pd.Series : Volatilidad rolling anualizada
        """
        return self.returns.rolling(window).std() * np.sqrt(periods)
    
    def get_risk_summary(self, confidence_level=0.95, risk_free_rate=0.01):
        """
        Retorna un resumen completo de métricas de riesgo
        
        Returns:
        --------
        dict : Resumen de riesgo
        """
        drawdown_series, max_dd = self.calculate_drawdown()
        
        return {
            'mean_return': self.returns.mean() * 252,
            'volatility': self.returns.std() * np.sqrt(252),
            'var_95_historical': self.calculate_var_historical(confidence_level),
            'var_95_parametric': self.calculate_var_parametric(confidence_level),
            'cvar_95': self.calculate_cvar(confidence_level),
            'max_drawdown': max_dd,
            'recovery_time_days': self.calculate_recovery_time(),
            'calmar_ratio': self.calculate_calmar_ratio(),
            'sortino_ratio': self.calculate_sortino_ratio(risk_free_rate=risk_free_rate),
            'omega_ratio': self.calculate_omega_ratio(),
            'skewness': self.returns.skew(),
            'kurtosis': self.returns.kurtosis(),
        }


class CorrelationAnalysis:
    """Análisis de correlaciones dinámicas entre activos"""
    
    def __init__(self, returns):
        """
        Inicializa el análisis de correlación
        
        Parameters:
        -----------
        returns : pd.DataFrame
            Retornos de múltiples activos
        """
        self.returns = returns
    
    def calculate_rolling_correlation(self, window=60):
        """
        Calcula correlación rolling entre activos
        
        Parameters:
        -----------
        window : int
            Tamaño de la ventana
            
        Returns:
        --------
        dict : Correlaciones rolling para cada par
        """
        correlations = {}
        assets = self.returns.columns
        
        for i, asset1 in enumerate(assets):
            for asset2 in assets[i+1:]:
                pair_name = f"{asset1}-{asset2}"
                correlations[pair_name] = self.returns[asset1].rolling(window).corr(
                    self.returns[asset2]
                )
        
        return correlations
    
    def detect_correlation_breakdowns(self, window=60, threshold=0.3):
        """
        Detecta cambios abruptos en correlación (importante para riesgo)
        
        Parameters:
        -----------
        window : int
            Tamaño de la ventana
        threshold : float
            Cambio mínimo para considerar un quiebre
            
        Returns:
        --------
        dict : Fechas de quiebres de correlación
        """
        rolling_corr = self.calculate_rolling_correlation(window)
        breakdowns = {}
        
        for pair, correlation in rolling_corr.items():
            breakdowns[pair] = correlation[abs(correlation.diff()) > threshold].index.tolist()
        
        return breakdowns
    
    def get_average_correlation(self, start_date=None, end_date=None):
        """
        Calcula correlación promedio en un período
        
        Returns:
        --------
        pd.DataFrame : Matriz de correlación
        """
        subset = self.returns
        if start_date:
            subset = subset[start_date:]
        if end_date:
            subset = subset[:end_date]
        
        return subset.corr()
