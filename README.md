# 📈 Sistema Integrado de Gestión de Riesgo y Optimización de Cartera: unified_portfolio_colab.py

Este repositorio contiene una herramienta avanzada en Python diseñada para el análisis cuantitativo, optimización y gestión de riesgos de carteras de inversión. El sistema integra el modelo de **Markowitz**, simulaciones de **Monte Carlo**, **Backtesting** con rebalanceo y pruebas de estrés en una única interfaz unificada.

No más adivinanzas con tu capital; deja que las matemáticas y el código hagan el trabajo pesado.

## ✨ Características Principales

* **Descarga de Datos Automatizada:** Integración con Yahoo Finance para obtener precios históricos y dividendos.
* **Métricas de Riesgo Exhaustivas:** Cálculo automático de Volatilidad, Ratio de Sharpe, Máximo Drawdown, VaR (Value at Risk) y CVaR (Expected Shortfall).
* **Optimización de Cartera:** Algoritmos para hallar carteras de Máximo Sharpe, Mínima Volatilidad o retornos objetivo.
* **Simulación de Monte Carlo:** Proyecciones estadísticas del valor futuro de la cartera basándose en rendimientos históricos.
* **Backtesting Realista:** Simulación de rendimiento histórico con frecuencias de rebalanceo personalizables (diario, semanal, mensual, etc.).
* **Comparación con Benchmarks:** Evaluación del desempeño frente a índices de referencia como el S&P 500 (SPY).
* **Reportes PDF Profesionales:** Generación automática de un informe con gráficos de fronteras eficientes, matrices de correlación y resultados de estrés.

---

## 🛠️ Requisitos e Instalación

Para ejecutar este proyecto, necesitarás Python 3.x y las siguientes bibliotecas:

```bash
pip install numpy pandas matplotlib seaborn scipy yfinance
```

---

## 📖 Guía de Uso Paso a Paso

### Opción 1: Ejecución en Google Colab (Recomendado)
1.  Crea un nuevo cuaderno en [Google Colab](https://colab.research.google.com/).
2.  Copia y pega el contenido del archivo `unified_portfolio_colab.txt` en una celda de código.
3.  Asegúrate de instalar las librerías mencionadas arriba en la primera celda (usando `!pip install ...`).
4.  Ejecuta la celda. El script descargará automáticamente los datos de los tickers configurados (por defecto: AAPL, MSFT, GOOGL, AMZN, TSLA).

### Opción 2: Uso Local o Personalizado
Si deseas integrar el código en tu propio flujo de trabajo, sigue estos pasos:

#### 1. Configurar los Activos
Define los tickers y el rango de fechas dentro del bloque `if __name__ == "__main__":`:
```python
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
start_date = '2023-01-01'
initial_capital = 100000
```

#### 2. Obtener los Datos e Inicializar el Gestor
El sistema utiliza el `DataFetcher` para limpiar y preparar los precios:
```python
fetcher = DataFetcher()
prices = fetcher.fetch_data(tickers, start_date=start_date)
unified_manager = UnifiedPortfolioManager(prices)
```

#### 3. Optimizar y Analizar
Puedes buscar la cartera ideal con una sola línea de código:
```python
# Optimizar para el máximo Ratio de Sharpe
optimal_portfolio = unified_manager.optimize_portfolio('sharpe')

# Ver el resumen de métricas (VaR, Retorno, Volatilidad)
summary = unified_manager.get_portfolio_summary()
```

#### 4. Ejecutar Pruebas de Estrés y Simulaciones
Evalúa cómo reaccionaría tu dinero ante una crisis financiera o una recesión:
```python
stress_test = unified_manager.stress_test()
mc_results = unified_manager.monte_carlo_simulation(initial_capital=100000)
```

#### 5. Exportar Resultados
Para obtener un archivo PDF con todos los gráficos (Frontera Eficiente, Correlaciones, Backtest):
```python
unified_manager.export_to_pdf('mi_reporte_inversion.pdf')
```

---

## 📊 Estructura del Código

El archivo principal se divide en tres componentes clave:
* **`DataFetcher`**: Maneja la conexión con la API de Yahoo Finance y la limpieza de datos MultiIndex.
* **`UnifiedPortfolioManager`**: El motor analítico que calcula retornos, volatilidades y optimiza pesos mediante programación cuadrática (SLSQP).
* **Módulo de Visualización**: Genera gráficos interactivos con Seaborn y Matplotlib para facilitar la interpretación de datos complejos.

---

## ⚠️ Advertencia de Riesgo
*Este software tiene fines educativos y de investigación. El rendimiento pasado no garantiza resultados futuros. Toda inversión conlleva riesgos de pérdida de capital.*

