"""
Módulo de Utilidades Compartidas
=================================

Funciones auxiliares para:
- Manipulación de datos
- Cálculos comunes
- Visualización
- Logging
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')
sns.set_style('darkgrid')


class DataProcessor:
    """Utilidades para procesar datos de portafolios"""
    
    @staticmethod
    def normalize_weights(weights):
        """Normaliza pesos para que sumen 1"""
        return weights / np.sum(weights)
    
    @staticmethod
    def calculate_portfolio_metrics(returns, weights, risk_free_rate=0.01):
        """Calcula métricas principales del portafolio"""
        portfolio_return = np.sum(returns.mean() * weights) * 252
        portfolio_volatility = np.sqrt(np.dot(weights, np.dot(returns.cov() * 252, weights)))
        sharpe = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return {
            'return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe': sharpe
        }
    
    @staticmethod
    def align_dataframes(*dfs):
        """Alinea múltiples DataFrames por índice común"""
        common_index = dfs[0].index
        for df in dfs[1:]:
            common_index = common_index.intersection(df.index)
        
        return tuple(df.loc[common_index] for df in dfs)


class VisualizationUtils:
    """Utilidades para visualización de portafolios"""
    
    @staticmethod
    def plot_portfolio_performance(portfolio_returns, title='Portfolio Performance'):
        """Gráfica de rendimiento acumulado"""
        cumulative = (1 + portfolio_returns).cumprod()
        
        plt.figure(figsize=(12, 6))
        cumulative.plot(title=title, label='Cumulative Return')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        return plt.gcf()
    
    @staticmethod
    def plot_drawdown(portfolio_returns, title='Drawdown Analysis'):
        """Gráfica de drawdown"""
        cumulative = (1 + portfolio_returns).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        
        plt.figure(figsize=(12, 6))
        drawdown.plot(title=title, color='red', alpha=0.7)
        plt.xlabel('Date')
        plt.ylabel('Drawdown')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        return plt.gcf()
    
    @staticmethod
    def plot_efficient_frontier(returns, weights_list=None):
        """Gráfica de frontera eficiente"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if weights_list:
            volatilities = []
            returns_vals = []
            for w in weights_list:
                ret = np.sum(returns.mean() * w) * 252
                vol = np.sqrt(np.dot(w, np.dot(returns.cov() * 252, w)))
                volatilities.append(vol)
                returns_vals.append(ret)
            
            ax.scatter(volatilities, returns_vals, alpha=0.5, s=10)
        
        ax.set_xlabel('Volatility')
        ax.set_ylabel('Expected Return')
        ax.set_title('Efficient Frontier')
        ax.grid(alpha=0.3)
        
        return fig
    
    @staticmethod
    def plot_correlation_heatmap(returns, title='Correlation Matrix'):
        """Heatmap de correlación"""
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(returns.corr(), annot=True, cmap='coolwarm', 
                   fmt='.2f', ax=ax, square=True)
        ax.set_title(title)
        plt.tight_layout()
        return fig


class Logger:
    """Utilidades de logging"""
    
    @staticmethod
    def log_metrics(metrics_dict, prefix=''):
        """Imprime métricas de forma formateada"""
        print(f"\n{prefix}")
        print("-" * 60)
        for key, value in metrics_dict.items():
            if isinstance(value, (float, np.floating)):
                if 'return' in key.lower() or 'volatility' in key.lower() or 'ratio' in key.lower():
                    print(f"  {key.replace('_', ' ').title():<30} {value*100:>10.2f}%")
                else:
                    print(f"  {key.replace('_', ' ').title():<30} {value:>10.4f}")
            else:
                print(f"  {key.replace('_', ' ').title():<30} {str(value):>10}")
        print("-" * 60)
    
    @staticmethod
    def log_portfolio_summary(prices, weights, risk_free_rate=0.01):
        """Registra un resumen del portafolio"""
        returns = prices.pct_change().dropna()
        metrics = DataProcessor.calculate_portfolio_metrics(returns, weights, risk_free_rate)
        
        print(f"\n📊 Portfolio Summary")
        print("-" * 60)
        print(f"  Assets: {', '.join(prices.columns)}")
        print(f"  Weights: {', '.join([f'{w:.2%}' for w in weights])}")
        print(f"  Expected Return (Annual): {metrics['return']:.2%}")
        print(f"  Volatility (Annual): {metrics['volatility']:.2%}")
        print(f"  Sharpe Ratio: {metrics['sharpe']:.4f}")
        print("-" * 60)
