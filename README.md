# 🏦 Sistema Integrado de Gestión y Optimización de Portafolios

**Gestionar y diversificar un portafolio de acuerdo a su data histórica y optimización respecto a su rentabilidad y riesgo**

---

## 📋 Descripción General

Este proyecto implementa un sistema completo y modular de análisis, optimización y gestión de riesgo para portafolios de inversión. Utiliza técnicas avanzadas de Machine Learning, teoría moderna de portafolios y análisis estadístico.

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

## 🎓 Guía Paso a Paso: Usar en Google Colab

Esta sección te guiará para ejecutar el sistema completamente en **Google Colab** sin necesidad de instalar nada localmente.

### **Paso 1: Crear un Notebook en Google Colab**

1. Ve a [https://colab.research.google.com/](https://colab.research.google.com/)
2. Haz clic en **"Nuevo Notebook"**
3. Renómbralo como: `Portfolio-Analysis`

---

### **Paso 2: Clonar el Repositorio**

En la primera celda de Colab, ejecuta:

```python
# Clonar el repositorio
!git clone https://github.com/kevinfr20/distribucion-de-portafolio.git
```

Luego, verifica que los archivos estén disponibles:

```python
import os
os.listdir('/content/distribucion-de-portafolio')
```

---

### **Paso 3: Instalar Dependencias**

Crea una nueva celda y ejecuta:

```python
# Instalar todas las dependencias
!pip install -r /content/distribucion-de-portafolio/requirements.txt -q
```

**Nota**: El `-q` silencia la salida para que sea más rápido.

Para comprobar que todo está instalado:

```python
import pandas as pd
import numpy as np
import tensorflow as tf
import yfinance as yf
print("✓ Todas las dependencias instaladas correctamente")
```

---

### **Paso 4: Importar el Módulo del Proyecto**

```python
# Agregar el repositorio al path de Python
import sys
sys.path.append('/content/distribucion-de-portafolio')

# Importar los módulos principales
from unified_portfolio_colab import DataFetcher, UnifiedPortfolioManager
from risk_metrics import AdvancedRiskMetrics
from backtesting import AdvancedBacktester
from adaptive_optimization import AdaptivePortfolioOptimizer
from ml_advanced_models import EnsemblePortfolioPredictor
from main import IntegratedPortfolioSystem

print("✓ Módulos importados exitosamente")
```

---

### **Paso 5: Ejecutar Análisis Completo (Recomendado para Principiantes)**

Esta es la forma **más simple** de usar todo el sistema:

```python
from datetime import datetime

# Definir los activos y período
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
start_date = '2023-01-01'
end_date = datetime.now().strftime('%Y-%m-%d')

print(f"📊 Analizando {len(tickers)} activos desde {start_date} hasta {end_date}")

# Crear el sistema integrado
system = IntegratedPortfolioSystem(
    tickers=tickers,
    start_date=start_date,
    end_date=end_date
)

# Ejecutar análisis completo
results = system.run_full_analysis(initial_capital=100000)

# Mostrar resultados
print("\n" + "="*60)
print("📈 RESULTADOS DEL ANÁLISIS")
print("="*60)
print(f"\n✓ Resumen de Riesgo:")
print(results['risk_summary'])
print(f"\n✓ Pesos Óptimos (Máximo Sharpe):")
print(results['optimal_weights'])
print(f"\n✓ Régimen de Mercado Detectado:")
print(results['regime'])
```

---

### **Paso 6: Análisis Paso a Paso (Para Usuarios Avanzados)**

Si prefieres mayor **control y flexibilidad**, sigue estos pasos:

#### **6.1 Descargar los Datos**

```python
# Crear fetcher y descargar datos
fetcher = DataFetcher()
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
prices = fetcher.fetch_data(
    tickers=tickers,
    start_date='2023-01-01',
    end_date='2026-05-18'
)

print(f"✓ Datos descargados: {prices.shape[0]} fechas, {prices.shape[1]} activos")
print(f"Últimas 5 precios:\n{prices.tail()}")
```

#### **6.2 Crear el Gestor de Portafolio**

```python
# Crear gestor
manager = UnifiedPortfolioManager(prices)

print(f"✓ Retorno promedio diario: {manager.returns.mean().mean():.4%}")
print(f"✓ Volatilidad: {manager.returns.std().mean():.4%}")

# Ver matriz de correlación
print("\n📊 Matriz de Correlación:")
print(manager.returns.corr())
```

#### **6.3 Análisis de Riesgo**

```python
# Crear analizador de riesgo
risk_analyzer = AdvancedRiskMetrics(manager.returns)

# Obtener resumen
risk_summary = risk_analyzer.get_risk_summary()

print("🎯 ANÁLISIS DE RIESGO:")
print("="*60)
print(f"VaR (95%): {risk_summary['var_95']:.4%}")
print(f"CVaR (95%): {risk_summary['cvar_95']:.4%}")
print(f"Máximo Drawdown: {risk_summary['max_drawdown']:.4%}")
print(f"Sharpe Ratio: {risk_summary['sharpe_ratio']:.4f}")
print(f"Sortino Ratio: {risk_summary['sortino_ratio']:.4f}")
```

#### **6.4 Optimizar el Portafolio**

```python
# Optimizar con diferentes criterios
print("🚀 OPTIMIZACIÓN DE PORTAFOLIOS:")
print("="*60)

# Máximo Sharpe
optimal_sharpe = manager.optimize_portfolio('sharpe')
print(f"\n1️⃣ Máximo Sharpe:")
print(f"   Sharpe Ratio: {optimal_sharpe['sharpe_ratio']:.4f}")
print(f"   Pesos:\n{optimal_sharpe['weights']}")

# Mínima Volatilidad
optimal_min_vol = manager.optimize_portfolio('volatility')
print(f"\n2️⃣ Mínima Volatilidad:")
print(f"   Volatilidad: {optimal_min_vol['volatility']:.4%}")
print(f"   Pesos:\n{optimal_min_vol['weights']}")

# Con restricciones
optimal_constrained = manager.optimize_with_constraints(
    criterion='sharpe',
    min_weight=0.05,
    max_weight=0.50
)
print(f"\n3️⃣ Máximo Sharpe (con restricciones):")
print(f"   Sharpe Ratio: {optimal_constrained['sharpe_ratio']:.4f}")
print(f"   Pesos:\n{optimal_constrained['weights']}")
```

#### **6.5 Backtesting**

```python
# Crear backtester
backtester = AdvancedBacktester(prices, manager.returns)

# Usar los pesos óptimos
weights = optimal_sharpe['weights']

# Walk-Forward Backtest
print("📉 BACKTESTING - WALK-FORWARD ANALYSIS:")
print("="*60)
results = backtester.walk_forward_backtest(weights)

print(f"Retorno Promedio: {results['avg_return']:.2%}")
print(f"Sharpe Promedio: {results['avg_sharpe']:.4f}")
print(f"Volatilidad Promedio: {results['avg_volatility']:.2%}")

# Análisis por período
print("\n📊 ANÁLISIS POR PERÍODO:")
period_analysis = backtester.time_period_analysis(weights)
print(period_analysis)
```

#### **6.6 Detección de Regímenes de Mercado**

```python
# Crear optimizador adaptativo
optimizer = AdaptivePortfolioOptimizer(prices, manager.returns)

# Detectar régimen actual
regime = optimizer.detect_market_regime()

print("🎯 RÉGIMEN DE MERCADO DETECTADO:")
print("="*60)
print(f"Régimen: {regime['regime']}")
print(f"Volatilidad: {regime['volatility']:.4%}")
print(f"Tendencia: {regime['trend']}")

# Obtener pesos adaptativos
adaptive_weights, info = optimizer.get_adaptive_weights()
print(f"\n💡 Pesos Adaptativos al Régimen:")
print(adaptive_weights)
```

#### **6.7 Predicción con Machine Learning**

```python
# Crear predictor ensemble
print("🤖 PREDICCIÓN CON MACHINE LEARNING:")
print("="*60)

portfolio_returns = manager.returns.mean(axis=1)
ensemble = EnsemblePortfolioPredictor(portfolio_returns, lookback=20)

# Entrenar
print("Entrenando modelos (esto puede tardar un momento)...")
ensemble.train()

# Predecir 30 días hacia adelante
predictions = ensemble.predict_future(days=30)

print(f"\n📈 Predicciones para los próximos 30 días:")
print(f"LSTM: {predictions.get('lstm', [])[-1]:.4%}")
print(f"Gradient Boosting: {predictions.get('gb', [])[-1]:.4%}")
print(f"Ensemble: {predictions.get('ensemble', [])[-1]:.4%}")

# Visualizar comparación
ensemble.plot_comparison(days=30)
```

---

### **Paso 7: Visualizaciones y Reportes**

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# 1. Desempeño histórico
fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# Retornos acumulados
cumulative_returns = (1 + manager.returns).cumprod()
cumulative_returns.plot(ax=axes[0, 0], title='Retornos Acumulados')
axes[0, 0].legend(loc='best')

# Volatilidad rolling
manager.returns.rolling(window=20).std().plot(ax=axes[0, 1], title='Volatilidad Rolling (20 días)')

# Matriz de correlación
sns.heatmap(manager.returns.corr(), annot=True, ax=axes[1, 0], cmap='coolwarm', center=0)
axes[1, 0].set_title('Matriz de Correlación')

# Distribución de retornos
manager.returns.mean().plot(kind='bar', ax=axes[1, 1], title='Retorno Promedio por Activo')

plt.tight_layout()
plt.savefig('portfolio_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

print("✓ Gráficos guardados como 'portfolio_analysis.png'")
```

---

### **Paso 8: Exportar Resultados**

```python
# Guardar resultados en CSV
import pandas as pd

# Matriz de correlación
correlation_df = manager.returns.corr()
correlation_df.to_csv('correlation_matrix.csv')

# Pesos óptimos
weights_df = pd.DataFrame({
    'Ticker': tickers,
    'Peso (%)': [w*100 for w in optimal_sharpe['weights']]
})
weights_df.to_csv('optimal_weights.csv', index=False)

# Resumen de riesgo
risk_df = pd.DataFrame(risk_summary, index=[0]).T
risk_df.to_csv('risk_summary.csv')

print("✓ Archivos exportados:")
print("  - correlation_matrix.csv")
print("  - optimal_weights.csv")
print("  - risk_summary.csv")

# Descargar archivos (opcional en Colab)
from google.colab import files
files.download('optimal_weights.csv')
print("✓ Archivo descargado")
```

---

### **Paso 9: Código Completo (Template Listo para Usar)**

```python
import sys
import importlib
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Force reload to pick up the DataFetcher merge fix
if 'unified_portfolio_colab' in sys.modules:
    importlib.reload(sys.modules['unified_portfolio_colab'])

from unified_portfolio_colab import DataFetcher, UnifiedPortfolioManager
from risk_metrics import AdvancedRiskMetrics
from backtesting import AdvancedBacktester

# CONFIGURACIÓN
TICKERS = ['AAPL', 'MSFT', 'UNACEMC1', 'GOOGL', 'AMZN']
START_DATE = '2023-01-01'
INITIAL_CAPITAL = 100000

print(f"📊 Iniciando análisis de portafolio final...")

# PASO 1: Descargar datos con la nueva lógica de alineación
fetcher = DataFetcher()
prices = fetcher.fetch_data(TICKERS, START_DATE)
print(f"✓ Datos procesados: {prices.shape[0]} fechas")
print(f"✓ Columnas con datos: {[col for col in prices.columns if prices[col].notnull().any()]}")

# PASO 2: Crear gestor y optimizar
manager = UnifiedPortfolioManager(prices)
optimal = manager.optimize_portfolio('sharpe')

# PASO 3: Análisis de riesgo
risk_analyzer = AdvancedRiskMetrics(manager.returns)
risk_summary = risk_analyzer.get_risk_summary()

# PASO 4: Mostrar Resultados
weights_df = pd.DataFrame({
    'Ticker': TICKERS,
    'Peso (%)': [optimal['weights'].get(ticker, 0) * 100 for ticker in TICKERS]
})

print("\n" + "="*50)
print("📋 RESULTADO FINAL - PESOS ÓPTIMOS")
print("="*50)
print(weights_df.to_string(index=False, formatters={'Peso (%)': '{:.2f}%'.format}))

print(f"\nSharpe Ratio del Portafolio: {optimal['sharpe_ratio']:.4f}")
if 'var_95_historical' in risk_summary:
    print(f"VaR Histórico (95%): {risk_summary['var_95_historical']:.2%}")

# Visualización rápida
prices.plot(figsize=(12, 6), title="Evolución de Precios Normalizada")
plt.ylabel("Precio")
plt.show()

# PASO 5: Backtesting
backtester = AdvancedBacktester(prices, manager.returns)
# Pass the optimization function to walk_forward_backtest
backtest_results = backtester.walk_forward_backtest(optimize_for_backtest)
print(f"✓ Backtesting completado")
print(f"   Retorno Promedio: {backtest_results['average_return']:.2%}")

```

---

### **Troubleshooting - Problemas Comunes en Colab**

| Problema | Solución |
|----------|----------|
| ❌ `ModuleNotFoundError: No module named 'tensorflow'` | Ejecuta: `!pip install tensorflow -q` |
| ❌ `ConnectionError` al descargar datos | Intenta con diferentes tickers o espera 5 minutos |
| ❌ `MemoryError` con demasiados datos | Reduce el número de activos o acorta el período |
| ❌ GPU no disponible | Activa GPU: Menú → Entorno de ejecución → Cambiar tipo → GPU |
| ❌ Gráficos no se muestran | Añade: `%matplotlib inline` al inicio |

---

### **Tips y Mejores Prácticas**

✅ **Usa GPU**: Ve a Entorno de ejecución → Cambiar tipo → Selecciona GPU (x5 más rápido)

✅ **Guarda tu notebook**: Colab autosave cada 30s, pero no confíes completamente

✅ **Descargar resultados**: Usa `files.download()` para guardar en tu PC

✅ **Compartir notebook**: Usa el botón Compartir en la esquina superior derecha

✅ **Período de sesión**: Colab cierra después de 12 horas inactivas

✅ **Para análisis largos**: Divide en celdas pequeñas para debug más fácil

---

