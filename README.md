# 🏦 Sistema Integrado de Gestión y Optimización de Portafolios

**Gestionar y diversificar un portafolio de acuerdo a su data histórica y optimización respecto a su rentabilidad y riesgo**

---

## 📋 Descripción General

Este proyecto implementa un sistema completo y modular de análisis, optimización y gestión de riesgo para portafolios de inversión. Utiliza técnicas avanzadas de Machine Learning, teoría moderna de portafolios y análisis cuantitativo de riesgo.

### ✨ Características Principales

✅ **Optimización de Portafolios**
- Máximo Sharpe Ratio
- Mínima Volatilidad  
- Retorno Objetivo
- Volatilidad Objetivo
- Restricciones personalizadas

✅ **Análisis Avanzado de Riesgo**
- Value at Risk (VaR) - Histórico, Paramétrico, Monte Carlo
- Conditional Value at Risk (CVaR/Expected Shortfall)
- Maximum Drawdown y análisis de recuperación
- Calmar Ratio, Sortino Ratio, Omega Ratio
- Volatilidad Predictiva
- Correlaciones Dinámicas

✅ **Backtesting Robusto**
- Walk-Forward Analysis (validación temporal)
- Análisis multi-período (Bull, Bear, Lateral)
- Simulaciones de Monte Carlo
- Métricas de rendimiento detalladas

✅ **Modelos de Machine Learning**
- LSTM para predicción de retornos
- Gradient Boosting
- Random Forest
- Ensemble Methods

✅ **Optimización Adaptativa**
- Rebalanceo dinámico basado en cambios de mercado
- Detección de regímenes de mercado
- Restricciones de riesgo automáticas

---

## 📁 Estructura Refactorizada del Proyecto

```
distribucion-de-portafolio/
│
├── unified_portfolio_colab.py      # Gestor principal de portafolios
│                                    # - DataFetcher
│                                    # - UnifiedPortfolioManager
│
├── risk_metrics.py                 # Cálculos avanzados de riesgo
│                                    # - AdvancedRiskMetrics
│                                    # - CorrelationAnalysis
│
├── backtesting.py                  # Validación robusta de estrategias
│                                    # - AdvancedBacktester
│
├── adaptive_optimization.py        # Optimización dinámica
│                                    # - AdaptivePortfolioOptimizer
│
├── ml_advanced_models.py           # Modelos de Machine Learning
│                                    # - LSTM, Gradient Boosting, Ensemble
│
├── utils.py                        # Utilidades compartidas
│                                    # - DataProcessor, VisualizationUtils
│
├── main.py                         # Script de integración completa
│                                    # - IntegratedPortfolioSystem
│
├── requirements.txt                # Dependencias
└── README.md                       # Este archivo
```

---

## 🚀 Instalación y Configuración

### Requisitos
- Python 3.8+
- pip

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/kevinfr20/distribucion-de-portafolio.git
cd distribucion-de-portafolio

# Instalar dependencias
pip install -r requirements.txt
```

### Dependencias Principales

```
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
scipy>=1.7.0
scikit-learn>=1.0.0
tensorflow>=2.8.0
yfinance>=0.1.70
```

---

## 💻 Uso Rápido

### Sistema Integrado Completo

```python
from main import IntegratedPortfolioSystem
from datetime import datetime

# Configuración
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
start_date = '2023-01-01'

# Ejecutar análisis completo
system = IntegratedPortfolioSystem(tickers, start_date)
results = system.run_full_analysis(initial_capital=100000)
```

### Módulos Individuales

#### 1. Análisis de Riesgo

```python
from unified_portfolio_colab import DataFetcher, UnifiedPortfolioManager
from risk_metrics import AdvancedRiskMetrics

# Descargar datos
fetcher = DataFetcher()
prices = fetcher.fetch_data(['AAPL', 'MSFT', 'GOOGL'])

# Crear gestor
manager = UnifiedPortfolioManager(prices)

# Análisis de riesgo
risk_analyzer = AdvancedRiskMetrics(manager.returns)
risk_summary = risk_analyzer.get_risk_summary()
```

#### 2. Optimización

```python
# Optimizar para Máximo Sharpe
optimal = manager.optimize_portfolio('sharpe')
print(f"Sharpe Ratio: {optimal['sharpe_ratio']:.4f}")
```

#### 3. Backtesting

```python
from backtesting import AdvancedBacktester

backtester = AdvancedBacktester(prices, manager.returns)
weights = {'AAPL': 0.3, 'MSFT': 0.3, 'GOOGL': 0.4}

results = backtester.walk_forward_backtest(weights)
print(f"Retorno promedio: {results['avg_return']:.2%}")
```

#### 4. Optimización Adaptativa

```python
from adaptive_optimization import AdaptivePortfolioOptimizer

optimizer = AdaptivePortfolioOptimizer(prices, manager.returns)
regime = optimizer.detect_market_regime()
adaptive_weights, info = optimizer.get_adaptive_weights()
```

#### 5. Predicción con ML

```python
from ml_advanced_models import EnsemblePortfolioPredictor

ensemble = EnsemblePortfolioPredictor(manager.returns.mean(axis=1), lookback=20)
ensemble_results = ensemble.train()
predictions = ensemble.predict_future(days=30)
```

---

## 📊 Módulos Detallados

### 1. **unified_portfolio_colab.py** - Gestor Principal

**DataFetcher**
- Descarga datos de Yahoo Finance
- Maneja MultiIndex de pandas
- Soporte para dividendos

**UnifiedPortfolioManager**
- Optimización de pesos
- Cálculo de métricas (Sharpe, Volatilidad, etc.)
- VaR y CVaR
- Stress testing
- Monte Carlo simulation
- Backtesting con rebalanceo
- Comparación con benchmarks

**Métodos principales:**
```python
manager.optimize_portfolio(criterion='sharpe')
manager.optimize_with_constraints(min_weight=0.05, max_weight=0.5)
manager.calculate_var(confidence_level=0.95)
manager.backtest_portfolio(weights, rebalance_freq='monthly')
manager.stress_test()
manager.monte_carlo_simulation(n_simulations=10000)
manager.export_to_pdf('reporte.pdf')
```

### 2. **risk_metrics.py** - Análisis Avanzado de Riesgo

**AdvancedRiskMetrics**
- VaR paramétrico e histórico
- CVaR (Expected Shortfall)
- Drawdown y recuperación
- Ratios: Calmar, Sortino, Omega
- Volatilidad rolling
- Skewness y Kurtosis

**CorrelationAnalysis**
- Correlación rolling
- Detección de quiebres de correlación
- Matriz de correlación temporal

**Métodos principales:**
```python
risk_metrics.calculate_var_historical(confidence_level=0.95)
risk_metrics.calculate_cvar(confidence_level=0.95)
risk_metrics.calculate_max_drawdown()
risk_metrics.calculate_calmar_ratio()
risk_metrics.calculate_sortino_ratio()
risk_metrics.get_risk_summary()
```

### 3. **backtesting.py** - Validación Robusta

**AdvancedBacktester**
- Walk-Forward Analysis (validación temporal)
- Análisis por período de mercado
- Validación con Monte Carlo
- Métricas rolling
- Análisis de sensibilidad

**Métodos principales:**
```python
backtester.walk_forward_backtest(weights)
backtester.time_period_analysis(weights)
backtester.montecarlo_validation(weights, n_simulations=1000)
backtester.rolling_performance_metrics(weights, window=63)
backtester.parameter_sensitivity(weights_range)
```

### 4. **adaptive_optimization.py** - Optimización Dinámica

**AdaptivePortfolioOptimizer**
- Detección de regímenes de mercado
- Rebalanceo automático
- Restricciones de riesgo adaptativas
- Integración con predicciones de ML

**Métodos principales:**
```python
optimizer.detect_market_regime()
optimizer.rebalance_on_signal(signal_type='volatility')
optimizer.apply_risk_constraints(max_drawdown=0.15)
optimizer.optimize_with_ml_predictions(predicted_returns, predicted_vol)
optimizer.get_adaptive_weights(regime_detection=True)
```

### 5. **ml_advanced_models.py** - Machine Learning

**LSTMPortfolioPredictor**
- Red neuronal recurrente
- Predicción de retornos futuros
- Training con validación

**GBPortfolioPredictor**
- Gradient Boosting
- Importancia de características

**EnsemblePortfolioPredictor**
- Combina LSTM, Gradient Boosting y Random Forest
- Promedia predicciones

**Métodos principales:**
```python
lstm.train(epochs=50, batch_size=32)
lstm.predict_future(days=30)
ensemble.predict_future(days=30)
ensemble.plot_comparison(days=30)
```

---

## 📈 Ejemplos Prácticos

### Ejemplo 1: Análisis Completo

```python
from main import IntegratedPortfolioSystem
from datetime import datetime

# Crear sistema
system = IntegratedPortfolioSystem(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
    start_date='2023-01-01',
    end_date=datetime.now().strftime('%Y-%m-%d')
)

# Ejecutar análisis completo
results = system.run_full_analysis(initial_capital=100000)

# Los resultados incluyen:
# - risk_summary
# - optimal_weights
# - regime (mercado actual)
# - backtest_results
# - regime_analysis
# - stress_test
```

### Ejemplo 2: Comparación de Estrategias

```python
import numpy as np
from backtesting import AdvancedBacktester

# Definir estrategias
strategies = {
    'equal_weight': np.array([0.25, 0.25, 0.25, 0.25]),
    'market_cap': np.array([0.4, 0.3, 0.2, 0.1]),
    'risk_parity': np.array([0.3, 0.25, 0.25, 0.2]),
}

backtester = AdvancedBacktester(prices, returns)

# Comparar en múltiples períodos
for strategy_name, weights in strategies.items():
    wf_results = backtester.walk_forward_backtest(weights)
    print(f"{strategy_name}:")
    print(f"  Avg Return: {wf_results['avg_return']:.2%}")
    print(f"  Avg Sharpe: {wf_results['avg_sharpe']:.4f}")
```

### Ejemplo 3: Predicción y Optimización

```python
from ml_advanced_models import EnsemblePortfolioPredictor
from adaptive_optimization import AdaptivePortfolioOptimizer

# Entrenar predictor
ensemble = EnsemblePortfolioPredictor(portfolio_returns, lookback=20)
ensemble.train()

# Predecir retornos futuros
predictions = ensemble.predict_future(days=30)

# Usar predicciones para optimizar
optimizer = AdaptivePortfolioOptimizer(prices, returns)
predicted_returns = predictions['ensemble'].mean()
predicted_vol = predictions['ensemble'].std()

adaptive_weights = optimizer.optimize_with_ml_predictions(
    predicted_returns=predicted_returns,
    predicted_volatility=predicted_vol
)
```

---

## 🎯 Guía de Selección por Perfil de Inversor

### Conservador
```python
# Portafolio de mínima volatilidad con límites
optimal = manager.optimize_portfolio(
    criterion='volatility',
    bounds=((0.05, 0.3), (0.05, 0.3), (0.05, 0.3), (0.35, 0.70))
)

# Máximo drawdown del 10%
weights = optimizer.apply_risk_constraints(max_drawdown=0.10)
```

### Moderado
```python
# Máximo Sharpe con concentración limitada
optimal = manager.optimize_with_constraints(
    criterion='sharpe',
    min_weight=0.05,
    max_weight=0.50
)
```

### Agresivo
```python
# Maximizar retorno con límite de volatilidad
optimal = manager.optimize_portfolio(
    criterion='return',
    bounds=((0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0))
)
```

---

## 📊 Métricas Principales

| Métrica | Fórmula | Interpretación |
|---------|---------|-----------------|
| **Sharpe Ratio** | (Return - Rf) / σ | Retorno ajustado por riesgo |
| **Sortino Ratio** | (Return - Rf) / σ_downside | Solo penaliza volatilidad negativa |
| **Calmar Ratio** | Annual Return / Max DD | Eficiencia de recuperación |
| **Omega Ratio** | Ganancias / Pérdidas | Ratio ponderado |
| **VaR** | Percentil X% | Pérdida máxima esperada |
| **CVaR** | Promedio de pérdidas > VaR | Peores casos esperados |

---

## ⚠️ Advertencias Importantes

**Este software es para fines educativos y de investigación:**
- El rendimiento pasado NO garantiza rendimientos futuros
- Los modelos de ML tienen limitaciones inherentes
- Toda inversión conlleva riesgo de pérdida de capital
- Realizar backtesting exhaustivo antes de implementar
- Consultar con asesor financiero profesional

---

## 🔄 Flujo de Uso Recomendado

1. **Descargar datos** → `DataFetcher.fetch_data()`
2. **Análisis inicial** → `UnifiedPortfolioManager.get_portfolio_summary()`
3. **Análisis de riesgo** → `AdvancedRiskMetrics.get_risk_summary()`
4. **Detectar régimen** → `AdaptivePortfolioOptimizer.detect_market_regime()`
5. **Optimizar** → `optimize_portfolio()` o `optimize_with_ml_predictions()`
6. **Validar** → `AdvancedBacktester.walk_forward_backtest()`
7. **Stress test** → `stress_test()` y `monte_carlo_simulation()`
8. **Reportar** → `export_to_pdf()`

---

## 📞 Soporte y Contribución

Para reportar bugs o sugerir mejoras:
- Abrir un Issue en GitHub
- Realizar un Pull Request con mejoras

---

**Última actualización**: Mayo 2026  
**Versión**: 2.0.0  
**Autor**: kevinfr20
