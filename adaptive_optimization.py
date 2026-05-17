"""
Módulo de Optimización Adaptativa de Portafolios
================================================

Este módulo proporciona:
- Rebalanceo dinámico basado en predicciones ML
- Restricciones de riesgo adaptativas
- Ajuste automático de pesos según cambios de mercado
- Integración con modelos de ML para predicciones
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import warnings

warnings.filterwarnings('ignore')


class AdaptivePortfolioOptimizer:
    """Optimización adaptativa que ajusta pesos dinámicamente"""
    
    def __init__(self, prices, returns, initial_weights=None):
        """
        Inicializa el optimizador adaptativo
        
        Parameters:
        -----------
        prices : pd.DataFrame
            Precios históricos
        returns : pd.DataFrame
            Retornos históricos
        initial_weights : array-like, optional
            Pesos iniciales
        """
        self.prices = prices
        self.returns = returns
        self.asset_names = prices.columns.tolist()
        self.num_assets = len(self.asset_names)
        
        if initial_weights is None:
            self.weights = np.array([1/self.num_assets] * self.num_assets)
        else:
            self.weights = np.array(initial_weights)
    
    def optimize_with_ml_predictions(self, predicted_returns, predicted_volatility, 
                                     confidence_scores=None, max_weight=0.5, 
                                     risk_tolerance=0.01):
        """
        Optimiza pesos usando predicciones de ML
        
        Parameters:
        -----------
        predicted_returns : array
            Retornos predichos por modelos ML
        predicted_volatility : array
            Volatilidad predicha
        confidence_scores : array, optional
            Scores de confianza de las predicciones
        max_weight : float
            Peso máximo por activo
        risk_tolerance : float
            Tolerancia al riesgo máxima
            
        Returns:
        --------
        array : Pesos optimizados
        """
        # Ajustar predicciones por confianza
        if confidence_scores is not None:
            adjusted_returns = predicted_returns * confidence_scores
        else:
            adjusted_returns = predicted_returns
        
        def objective(w):
            # Maximizar retorno predicho / riesgo
            portfolio_return = np.sum(w * adjusted_returns)
            portfolio_volatility = np.sqrt(np.sum((w ** 2) * (predicted_volatility ** 2)))
            return -portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'ineq', 'fun': lambda x: risk_tolerance - np.sqrt(np.sum((x ** 2) * (predicted_volatility ** 2)))}
        )
        
        bounds = tuple((0, max_weight) for _ in range(self.num_assets))
        
        result = minimize(objective, self.weights, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            self.weights = result.x
            return result.x
        else:
            return self.weights
    
    def rebalance_on_signal(self, signal_type='volatility', threshold=0.2):
        """
        Rebalancea el portafolio cuando se detectan cambios de régimen
        
        Parameters:
        -----------
        signal_type : str
            'volatility', 'correlation', 'drawdown'
        threshold : float
            Umbral para activar rebalanceo
            
        Returns:
        --------
        bool : Si se realizó rebalanceo
        dict : Información del rebalanceo
        """
        should_rebalance = False
        signal_value = None
        
        if signal_type == 'volatility':
            current_volatility = self.returns.iloc[-20:].std().mean() * np.sqrt(252)
            historical_volatility = self.returns.std().mean() * np.sqrt(252)
            signal_value = current_volatility / historical_volatility
            should_rebalance = abs(signal_value - 1) > threshold
            
        elif signal_type == 'correlation':
            current_corr = self.returns.iloc[-20:].corr().values.mean()
            historical_corr = self.returns.corr().values.mean()
            signal_value = abs(current_corr - historical_corr)
            should_rebalance = signal_value > threshold
            
        elif signal_type == 'drawdown':
            cumulative = (1 + self.returns.iloc[-60:]).cumprod()
            peak = cumulative.expanding().max()
            drawdown = ((cumulative - peak) / peak).min().min()
            signal_value = abs(drawdown)
            should_rebalance = signal_value > threshold
        
        return {
            'should_rebalance': should_rebalance,
            'signal_type': signal_type,
            'signal_value': signal_value,
            'threshold': threshold
        }
    
    def apply_risk_constraints(self, max_drawdown=0.15, max_volatility=0.25, 
                               min_diversification=0.1):
        """
        Aplica restricciones de riesgo automáticas
        
        Parameters:
        -----------
        max_drawdown : float
            Máximo drawdown permitido
        max_volatility : float
            Volatilidad máxima
        min_diversification : float
            Mínimo índice de diversificación
            
        Returns:
        --------
        array : Pesos ajustados con restricciones
        """
        cov_matrix = self.returns.cov()
        
        def objective(w):
            return np.sum(self.returns.mean() * w) * 252
        
        def volatility_constraint(w):
            vol = np.sqrt(np.dot(w, np.dot(cov_matrix * 252, w)))
            return max_volatility - vol
        
        def diversification_constraint(w):
            herfindahl = np.sum(w ** 2)
            return (1 / self.num_assets) - herfindahl
        
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'ineq', 'fun': volatility_constraint},
            {'type': 'ineq', 'fun': diversification_constraint}
        )
        
        bounds = tuple((0, 1) for _ in range(self.num_assets))
        
        result = minimize(lambda w: -objective(w), self.weights, 
                         method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            self.weights = result.x
            return result.x
        else:
            return self.weights
    
    def detect_market_regime(self, window=60):
        """
        Detecta cambios de régimen de mercado
        
        Returns:
        --------
        dict : Información de régimen actual
        """
        recent_returns = self.returns.iloc[-window:]
        recent_mean = recent_returns.mean().mean() * 252
        recent_vol = recent_returns.std().mean() * np.sqrt(252)
        
        historical_mean = self.returns.mean().mean() * 252
        historical_vol = self.returns.std().mean() * np.sqrt(252)
        
        # Clasificar régimen
        if recent_mean > historical_mean and recent_vol < historical_vol:
            regime = 'GROWTH'
        elif recent_mean < historical_mean and recent_vol > historical_vol:
            regime = 'STRESS'
        elif recent_mean > historical_mean and recent_vol > historical_vol:
            regime = 'VOLATILE_POSITIVE'
        elif recent_mean < historical_mean and recent_vol < historical_vol:
            regime = 'STABLE_NEGATIVE'
        else:
            regime = 'NEUTRAL'
        
        return {
            'regime': regime,
            'recent_return': recent_mean,
            'recent_volatility': recent_vol,
            'historical_return': historical_mean,
            'historical_volatility': historical_vol,
            'return_change': (recent_mean - historical_mean) / historical_mean if historical_mean != 0 else 0,
            'volatility_change': (recent_vol - historical_vol) / historical_vol if historical_vol != 0 else 0
        }
    
    def get_adaptive_weights(self, ml_predictions=None, regime_detection=True):
        """
        Calcula pesos adaptativos combinando múltiples señales
        
        Returns:
        --------
        array : Pesos adaptativos
        dict : Información de optimización
        """
        info = {}
        
        # Detectar régimen
        if regime_detection:
            regime = self.detect_market_regime()
            info['regime'] = regime
            
            # Ajustar pesos según régimen
            if regime['regime'] == 'GROWTH':
                # Más agresivo en crecimiento
                max_weight = 0.6
                risk_tolerance = 0.02
            elif regime['regime'] == 'STRESS':
                # Más conservador en estrés
                max_weight = 0.3
                risk_tolerance = 0.01
            else:
                max_weight = 0.5
                risk_tolerance = 0.015
        
        # Aplicar restricciones de riesgo
        optimized_weights = self.apply_risk_constraints(max_volatility=0.25)
        info['optimized_weights'] = optimized_weights
        
        return optimized_weights, info
