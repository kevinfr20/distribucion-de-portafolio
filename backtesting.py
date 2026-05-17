"""
Módulo de Backtesting Robusto para Portafolios
==============================================

Este módulo proporciona:
- Backtesting con walk-forward analysis
- Cross-validation temporal
- Análisis de diferentes períodos de mercado
- Rebalanceo dinámico
- Métricas de rendimiento detalladas
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class AdvancedBacktester:
    """Backtesting avanzado con análisis temporal"""
    
    def __init__(self, prices, returns=None):
        """
        Inicializa el backtester
        
        Parameters:
        -----------
        prices : pd.DataFrame
            Precios históricos
        returns : pd.DataFrame, optional
            Retornos precalculados
        """
        self.prices = prices
        self.returns = returns if returns is not None else prices.pct_change().dropna()
        self.asset_names = prices.columns.tolist()
    
    def walk_forward_backtest(self, weights_func, train_window=252, test_window=63, rebalance_freq='monthly'):
        """
        Realiza backtesting con walk-forward analysis
        (Entrenamiento -> Test -> Avance)
        
        Parameters:
        -----------
        weights_func : callable
            Función que calcula pesos basada en retornos históricos
        train_window : int
            Días de entrenamiento
        test_window : int
            Días de prueba
        rebalance_freq : str
            Frecuencia de rebalanceo
            
        Returns:
        --------
        dict : Resultados del backtesting
        """
        results = []
        positions = 0
        
        for i in range(train_window, len(self.returns) - test_window, test_window):
            # Período de entrenamiento
            train_returns = self.returns.iloc[i-train_window:i]
            
            # Calcular pesos
            weights = weights_func(train_returns)
            
            # Período de prueba
            test_returns = self.returns.iloc[i:i+test_window]
            
            # Simular portafolio
            portfolio_returns = (test_returns * weights).sum(axis=1)
            cumulative_return = (1 + portfolio_returns).prod() - 1
            annual_volatility = portfolio_returns.std() * np.sqrt(252)
            sharpe = portfolio_returns.mean() * 252 / annual_volatility if annual_volatility > 0 else 0
            
            results.append({
                'period_start': test_returns.index[0],
                'period_end': test_returns.index[-1],
                'cumulative_return': cumulative_return,
                'annual_volatility': annual_volatility,
                'sharpe_ratio': sharpe,
                'weights': weights,
                'portfolio_returns': portfolio_returns
            })
            
            positions += 1
        
        return {
            'results': results,
            'total_positions': positions,
            'average_return': np.mean([r['cumulative_return'] for r in results]),
            'average_volatility': np.mean([r['annual_volatility'] for r in results]),
            'average_sharpe': np.mean([r['sharpe_ratio'] for r in results])
        }
    
    def market_regime_backtest(self, weights, initial_capital=10000, rebalance_freq='monthly'):
        """
        Backtesting analizando diferentes regímenes de mercado
        
        Returns:
        --------
        dict : Rendimiento por régimen de mercado
        """
        # Identificar regímenes (Toro/Oso) basado en SMA
        sma_50 = self.prices.mean(axis=1).rolling(50).mean()
        bull_market = self.prices.mean(axis=1) > sma_50
        
        bull_returns = self.returns[bull_market].mean(axis=1)
        bear_returns = self.returns[~bull_market].mean(axis=1)
        
        bull_portfolio = bull_returns.sum() if len(bull_returns) > 0 else 0
        bear_portfolio = bear_returns.sum() if len(bear_returns) > 0 else 0
        
        return {
            'bull_market': {
                'cumulative_return': bull_portfolio,
                'periods': len(bull_returns),
                'volatility': bull_returns.std() * np.sqrt(252) if len(bull_returns) > 0 else 0
            },
            'bear_market': {
                'cumulative_return': bear_portfolio,
                'periods': len(bear_returns),
                'volatility': bear_returns.std() * np.sqrt(252) if len(bear_returns) > 0 else 0
            }
        }
    
    def get_backtest_metrics(self, portfolio_returns, initial_capital=10000):
        """
        Calcula métricas detalladas de backtesting
        
        Parameters:
        -----------
        portfolio_returns : pd.Series
            Retornos del portafolio
        initial_capital : float
            Capital inicial
            
        Returns:
        --------
        dict : Métricas de rendimiento
        """
        cumulative_returns = (1 + portfolio_returns).cumprod()
        final_value = initial_capital * cumulative_returns.iloc[-1]
        total_return = cumulative_returns.iloc[-1] - 1
        annual_return = (cumulative_returns.iloc[-1]) ** (252 / len(portfolio_returns)) - 1
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe = annual_return / annual_volatility if annual_volatility > 0 else 0
        
        # Drawdown
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min()
        
        # Métricas adicionales
        positive_returns = (portfolio_returns > 0).sum() / len(portfolio_returns)
        avg_win = portfolio_returns[portfolio_returns > 0].mean() if (portfolio_returns > 0).any() else 0
        avg_loss = portfolio_returns[portfolio_returns < 0].mean() if (portfolio_returns < 0).any() else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else np.inf
        
        return {
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'positive_returns_pct': positive_returns,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
    
    def compare_strategies(self, strategies_dict, initial_capital=10000):
        """
        Compara múltiples estrategias de rebalanceo
        
        Parameters:
        -----------
        strategies_dict : dict
            {nombre_estrategia: pesos_array}
        initial_capital : float
            Capital inicial
            
        Returns:
        --------
        dict : Comparación de estrategias
        """
        comparison = {}
        
        for strategy_name, weights in strategies_dict.items():
            portfolio_returns = (self.returns * weights).sum(axis=1)
            metrics = self.get_backtest_metrics(portfolio_returns, initial_capital)
            comparison[strategy_name] = metrics
        
        return comparison
