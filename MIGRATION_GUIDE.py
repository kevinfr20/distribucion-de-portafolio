"""
GUÍA DE IMPLEMENTACIÓN Y MIGRACIÓN
===================================

Instrucciones paso a paso para integrar el nuevo sistema de múltiples proveedores
de datos con el código existente de UnifiedPortfolioManager.
"""

# ==================== PASO 1: INSTALACIÓN DE DEPENDENCIAS ====================

"""
REQUISITOS PREVIOS
==================

Python: >= 3.8
pip: >= 21.0

INSTALACIÓN RÁPIDA
==================

1. Clonar el repositorio (ya hecho):
   
   cd distribucion-de-portafolio

2. Instalar dependencias:
   
   pip install -r requirements.txt

3. Verificar instalación:
   
   python -c "import pandas, numpy, yfinance, requests; print('✅ Dependencias OK')"


ARCHIVO requirements.txt (CREAR SI NO EXISTE)
==============================================

numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
scipy>=1.7.0
yfinance>=0.1.70
requests>=2.26.0
python-dotenv>=0.19.0

Para instalar:

pip install -r requirements.txt


VERIFICAR INSTALACIÓN DE MÓDULOS
================================

python -c "
from data_providers import BaseDataProvider, YahooFinanceProvider, BVLDataProvider, TradingEconomicsProvider, DataProviderFactory
from data_fetcher_integration import DataFetcher
from unified_portfolio_colab import UnifiedPortfolioManager
print('✅ Todos los módulos están disponibles')
"
"""


# ==================== PASO 2: ESTRUCTURA DE ARCHIVOS ====================

"""
ESTRUCTURA RECOMENDADA DEL PROYECTO
====================================

distribucion-de-portafolio/
│
├── unified_portfolio_colab.py          (Original, SIN CAMBIOS)
│
├── data_providers.py                   (NUEVO: Proveedores abstractos)
│   ├── BaseDataProvider (clase abstracta)
│   ├── YahooFinanceProvider
│   ├── BVLDataProvider
│   ├── TradingEconomicsProvider
│   └── DataProviderFactory
│
├── data_fetcher_integration.py         (NUEVO: Wrapper y utilidades)
│   ├── DataFetcher (compatible hacia atrás)
│   ├── create_portfolio_from_mixed_tickers()
│   └── display_data_provider_summary()
│
├── ARCHITECTURE_GUIDE.py               (NUEVO: Documentación)
│   └── Documentación técnica completa
│
├── MIGRATION_GUIDE.py                  (NUEVO: Este archivo)
│   └── Instrucciones de implementación
│
├── requirements.txt                    (NUEVO: Dependencias)
│
├── .env.example                        (NUEVO: Template de credenciales)
│
└── examples/
    ├── example_global_portfolio.py     (NUEVO: Ejemplo 1)
    ├── example_peru_portfolio.py       (NUEVO: Ejemplo 2)
    └── example_mixed_portfolio.py      (NUEVO: Ejemplo 3)
"""


# ==================== PASO 3: CONFIGURACIÓN DE CREDENCIALES ====================

"""
ARCHIVO .env (CREAR EN LA RAÍZ)
================================

1. Crear archivo .env:

   cat > .env << EOF
   BVL_API_KEY=tu_clave_aqui
   TRADING_ECONOMICS_TOKEN=tu_token_aqui
   EOF

2. Alternativa: Usar .env.example como template:

   cp .env.example .env
   # Editar .env con tus credenciales

3. Cargar en Python:

   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   bvl_key = os.environ.get('BVL_API_KEY')
   te_token = os.environ.get('TRADING_ECONOMICS_TOKEN')


ARCHIVO .env.example (CREAR PARA SEGURIDAD)
============================================

# API de la Bolsa de Valores de Lima
# Obtener en: https://www.bvl.com.pe/desarrolladores
BVL_API_KEY=your_bvl_api_key_here

# API de Trading Economics
# Obtener en: https://tradingeconomics.com/api
TRADING_ECONOMICS_TOKEN=your_trading_economics_token_here

# NOTA: No versionar .env en Git (agregar a .gitignore)


AGREGAR A .gitignore
====================

echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.pyo" >> .gitignore
echo ".DS_Store" >> .gitignore
"""


# ==================== PASO 4: VALIDACIÓN DEL SETUP ====================

"""
SCRIPT DE VALIDACIÓN
====================

Crear archivo: validate_setup.py

---

from data_providers import DataProviderFactory
from data_fetcher_integration import DataFetcher
from unified_portfolio_colab import UnifiedPortfolioManager
import os
from dotenv import load_dotenv

def validate_setup():
    print("\\n" + "="*80)
    print("🔍 VALIDACIÓN DEL SETUP")
    print("="*80 + "\\n")
    
    # 1. Verificar módulos
    print("1️⃣  Verificando módulos...")
    try:
        from data_providers import (
            BaseDataProvider, YahooFinanceProvider, 
            BVLDataProvider, TradingEconomicsProvider, DataProviderFactory
        )
        from data_fetcher_integration import DataFetcher
        from unified_portfolio_colab import UnifiedPortfolioManager
        print("   ✅ Todos los módulos importan correctamente\\n")
    except ImportError as e:
        print(f"   ❌ Error de importación: {e}\\n")
        return False
    
    # 2. Verificar DataProvider Factory
    print("2️⃣  Verificando DataProviderFactory...")
    try:
        factory = DataProviderFactory()
        assert factory.identify_market('AAPL') == 'yahoo'
        assert factory.identify_market('ALICORC1.HE') == 'bvl'
        assert factory.identify_market('SPBLPGPT') == 'trading_economics'
        print("   ✅ Factory funciona correctamente\\n")
    except Exception as e:
        print(f"   ❌ Error en Factory: {e}\\n")
        return False
    
    # 3. Verificar DataFetcher
    print("3️⃣  Verificando DataFetcher...")
    try:
        fetcher = DataFetcher()
        info = fetcher.get_market_info(['AAPL', 'ALICORC1.HE', 'SPBLPGPT'])
        assert len(info) == 3
        print("   ✅ DataFetcher funciona correctamente\\n")
    except Exception as e:
        print(f"   ❌ Error en DataFetcher: {e}\\n")
        return False
    
    # 4. Verificar conexión con Yahoo Finance
    print("4️⃣  Verificando conexión con Yahoo Finance...")
    try:
        data = fetcher.fetch_data_dynamic(['AAPL'], start_date='2024-01-01', end_date='2024-01-31')
        assert not data.empty, "No se descargaron datos"
        assert 'Close' in data.columns, "Falta columna Close"
        print(f"   ✅ Yahoo Finance funciona ({len(data)} registros descargados)\\n")
    except Exception as e:
        print(f"   ⚠️  Error al conectar con Yahoo Finance: {e}\\n")
        print("      (Esto podría deberse a problemas de red o de API)")
    
    # 5. Verificar credenciales
    print("5️⃣  Verificando credenciales de BVL...")
    load_dotenv()
    bvl_key = os.environ.get('BVL_API_KEY')
    if bvl_key and bvl_key != 'your_bvl_api_key_here':
        print("   ✅ BVL_API_KEY configurada\\n")
    else:
        print("   ⚠️  BVL_API_KEY no configurada (optional para Yahoo Finance)\\n")
    
    print("6️⃣  Verificando credenciales de Trading Economics...")
    te_token = os.environ.get('TRADING_ECONOMICS_TOKEN')
    if te_token and te_token != 'your_trading_economics_token_here':
        print("   ✅ TRADING_ECONOMICS_TOKEN configurada\\n")
    else:
        print("   ⚠️  TRADING_ECONOMICS_TOKEN no configurada (optional)\\n")
    
    print("="*80)
    print("✅ VALIDACIÓN COMPLETADA EXITOSAMENTE")
    print("="*80 + "\\n")
    return True

if __name__ == "__main__":
    validate_setup()

---

Ejecutar:

python validate_setup.py
"""


# ==================== PASO 5: MIGRATION CHECKLIST ====================

"""
LISTA DE VERIFICACIÓN PARA MIGRACIÓN
====================================

ANTES DE LA MIGRACIÓN:
□ Hacer backup del código original (unified_portfolio_colab.py)
□ Tener los archivos de datos históricos disponibles
□ Documentar todos los scripts que usan DataFetcher

INSTALACIÓN:
□ Crear requirements.txt
□ pip install -r requirements.txt
□ Copiar data_providers.py al directorio
□ Copiar data_fetcher_integration.py al directorio
□ Crear .env.example
□ Crear .env con credenciales (si aplica)

VALIDACIÓN:
□ Ejecutar validate_setup.py
□ Verificar que todos los módulos importan
□ Probar descarga desde Yahoo Finance
□ (Opcional) Probar descarga desde BVL con credenciales
□ (Opcional) Probar descarga desde Trading Economics

COMPATIBILIDAD HACIA ATRÁS:
□ Código existente usa DataFetcher.fetch_data() ✓ Funciona
□ UnifiedPortfolioManager no necesita cambios ✓ Funciona
□ Tests unitarios de portfolio ✓ Pasan

NUEVA FUNCIONALIDAD:
□ Probar descarga de tickers peruanos (si tienes credenciales)
□ Probar descarga mixta (global + perú)
□ Probar display_data_provider_summary()
□ Crear portafolios mixtos

DOCUMENTACIÓN:
□ Actualizar README.md del proyecto
□ Documentar credenciales requeridas
□ Crear ejemplos de uso
□ Actualizar docstrings en código antiguo si aplica

TESTING:
□ Tests unitarios para data_providers.py
□ Tests unitarios para data_fetcher_integration.py
□ Tests de integración con UnifiedPortfolioManager
□ Tests de manejo de errores

DESPLIEGUE:
□ Revisar permisos de archivos
□ Verificar .gitignore incluye .env
□ Commit y push a repositorio
□ Tag de versión (si aplica)
□ Notificar a equipo sobre cambios
"""


# ==================== PASO 6: EJEMPLOS RÁPIDOS ====================

"""
EJEMPLO 1: MANTENER CÓDIGO EXISTENTE (SIN CAMBIOS)
===================================================

# Tu código existente sigue funcionando exactamente igual:

from data_fetcher_integration import DataFetcher  # Cambiar import
from unified_portfolio_colab import UnifiedPortfolioManager

# Descargar datos (interfaz original)
prices = DataFetcher.fetch_data(
    ['AAPL', 'MSFT', 'GOOGL'],
    start_date='2023-01-01'
)

# Crear portafolio (sin cambios)
portfolio = UnifiedPortfolioManager(prices)

# Optimizar (sin cambios)
result = portfolio.optimize_portfolio('sharpe')

# ✅ FUNCIONA IGUAL


EJEMPLO 2: USAR NUEVA FUNCIONALIDAD (TICKERS PERUANOS)
=======================================================

from data_fetcher_integration import DataFetcher
from unified_portfolio_colab import UnifiedPortfolioManager
import os
from dotenv import load_dotenv

# Cargar credenciales
load_dotenv()
bvl_key = os.environ.get('BVL_API_KEY')

# Crear fetcher con credenciales
fetcher = DataFetcher(bvl_api_key=bvl_key)

# Descargar datos peruanos
prices = fetcher.fetch_data_dynamic(
    ['ALICORC1.HE', 'VOLCABC1.HE', 'FERREYCORP1.HE'],
    start_date='2023-01-01',
    end_date='2024-12-31'
)

# Crear portafolio
portfolio = UnifiedPortfolioManager(prices)

# Optimizar
result = portfolio.optimize_portfolio('sharpe')

print(f"Retorno: {result['expected_return']*100:.2f}%")
print(f"Pesos: {result['weights']}")


EJEMPLO 3: PORTAFOLIO MIXTO (GLOBAL + PERÚ)
============================================

from data_fetcher_integration import DataFetcher, display_data_provider_summary
from unified_portfolio_colab import UnifiedPortfolioManager
import os
from dotenv import load_dotenv

load_dotenv()
fetcher = DataFetcher(bvl_api_key=os.environ.get('BVL_API_KEY'))

# Mostrar qué proveedor se usa para cada ticker
tickers = ['AAPL', 'MSFT', 'ALICORC1.HE', 'VOLCABC1.HE', 'SPBLPGPT']
display_data_provider_summary(tickers)

# Descargar datos
prices = fetcher.fetch_data_dynamic(
    tickers,
    start_date='2023-01-01',
    end_date='2024-12-31'
)

# Crear portafolio con pesos específicos
weights = [0.3, 0.3, 0.2, 0.15, 0.05]  # 30% AAPL, 30% MSFT, etc.
portfolio = UnifiedPortfolioManager(prices, weights=weights)

# Ver resumen
summary = portfolio.get_portfolio_summary()
print(f"Activos: {summary['assets']}")
print(f"Retorno esperado: {summary['expected_return']*100:.2f}%")
print(f"Volatilidad: {summary['volatility']*100:.2f}%")
print(f"Sharpe Ratio: {summary['sharpe_ratio']:.4f}")

# Optimizar para máximo Sharpe
optimal = portfolio.optimize_portfolio('sharpe')
print(f"\\nPesos óptimos:")
for asset, weight in optimal['weights'].items():
    print(f"  {asset}: {weight*100:.1f}%")
"""


# ==================== PASO 7: SOLUCIÓN DE PROBLEMAS ====================

"""
PROBLEMAS COMUNES Y SOLUCIONES
==============================

PROBLEMA 1: ModuleNotFoundError: No module named 'data_providers'
─────────────────────────────────────────────────────────────────
Causa: El archivo data_providers.py no está en el directorio correcto
Solución:
1. Verificar que data_providers.py esté en la raíz del proyecto
2. python -c "import sys; print(sys.path)" para ver rutas de búsqueda
3. Agregar a PYTHONPATH: export PYTHONPATH=$PYTHONPATH:$(pwd)

PROBLEMA 2: ConnectionError: Error de conexión a BVL/Trading Economics
────────────────────────────────────────────────────────────────────
Causa: Sin internet o API no disponible
Solución:
1. Verificar conexión: ping google.com
2. Verificar que la URL de la API es correcta
3. Verificar que el firewall/proxy no bloquea
4. Intentar con un VPN si está geobloqueado

PROBLEMA 3: 401 Unauthorized - API Key inválida
────────────────────────────────────────────────
Causa: BVL_API_KEY no válida o expirada
Solución:
1. Verificar que .env tiene la clave correcta
2. Verificar que no hay espacios en blanco
3. Obtener nueva clave de https://www.bvl.com.pe/desarrolladores
4. Actualizar .env con la nueva clave

PROBLEMA 4: DataFrame vacío - No hay datos
───────────────────────────────────────────
Causa: Ticker no encontrado o rango de fechas sin datos
Solución:
1. Verificar que el ticker es correcto (ALICORC1.HE, no ALICORP)
2. Verificar que las fechas son válidas (start < end)
3. Verificar que hay datos para ese período
4. Probar con un ticker conocido (AAPL)

PROBLEMA 5: ImportError: cannot import name 'UnifiedPortfolioManager'
──────────────────────────────────────────────────────────────────
Causa: unified_portfolio_colab.py no está en el directorio
Solución:
1. Verificar que unified_portfolio_colab.py existe
2. Verificar que no hay errores de sintaxis en ese archivo
3. python -c "from unified_portfolio_colab import UnifiedPortfolioManager"

PROBLEMA 6: TypeError: 'NoneType' object is not subscriptable
─────────────────────────────────────────────────────────────
Causa: Método retornó None en lugar de DataFrame
Solución:
1. Verificar logs para ver qué proveedor se usó
2. Verificar que el proveedor no tuvo error
3. Usar display_data_provider_summary() para debuggear
4. Aumentar nivel de logging: logging.basicConfig(level=logging.DEBUG)


LOGS ÚTILES PARA DEBUGGING
==========================

Ver logs detallados:

    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    fetcher = DataFetcher()
    data = fetcher.fetch_data_dynamic(['AAPL'])

Salida esperada:

    DEBUG:YahooFinanceProvider:Realizando descarga de AAPL
    INFO:YahooFinanceProvider:📥 Descargando AAPL desde Yahoo Finance
    DEBUG:YahooFinanceProvider:Procesando respuesta de Yahoo Finance
    INFO:YahooFinanceProvider:✅ 252 registros descargados para AAPL
"""


# ==================== PASO 8: PRÓXIMOS PASOS ====================

"""
DESPUÉS DE LA MIGRACIÓN
=======================

1. TESTING EN PRODUCCIÓN
   ─────────────────────
   □ Probar con datos reales
   □ Monitorear performance
   □ Recopilar feedback del equipo
   □ Documentar issues

2. OPTIMIZACIONES
   ───────────────
   □ Implementar caché de datos
   □ Agregar descargas en paralelo
   □ Implementar retry automático

3. EXTENSIONES
   ────────────
   □ Agregar nuevo proveedor (ej: Crypto)
   □ Integrar datos en tiempo real
   □ Agregar soporte para opciones/futuros

4. MONITOREO
   ──────────
   □ Alertas si API falla
   □ Métricas de uso
   □ Dashboards de performance

5. DOCUMENTACIÓN
   ──────────────
   □ Actualizar guías internas
   □ Crear video tutorial
   □ Escribir blog post sobre la arquitectura


RECURSOS ÚTILES
===============

Documentación oficial:
- pandas: https://pandas.pydata.org/docs/
- yfinance: https://yfinance.readthedocs.io/
- requests: https://requests.readthedocs.io/

Patrones de diseño:
- Strategy Pattern: https://refactoring.guru/design-patterns/strategy
- Factory Pattern: https://refactoring.guru/design-patterns/factory-method
- ABC (Abstract Base Classes): https://docs.python.org/3/library/abc.html

APIs:
- BVL: https://www.bvl.com.pe/desarrolladores
- Trading Economics: https://tradingeconomics.com/api
- Yahoo Finance: https://finance.yahoo.com

Nuestro repositorio:
- GitHub: https://github.com/kevinfr20/distribucion-de-portafolio
"""


# ==================== RESUMEN ====================

print("""
╔════════════════════════════════════════════════════════════════════╗
║     GUÍA DE MIGRACIÓN - RESUMEN EJECUTIVO                         ║
╚════════════════════════════════════════════════════════════════════╝

✅ PASOS A SEGUIR:

1. 📦 Instalar dependencias: pip install -r requirements.txt
2. 📂 Copiar archivos: data_providers.py, data_fetcher_integration.py
3. 🔐 Configurar credenciales: Crear .env con claves
4. ✔️  Validar setup: python validate_setup.py
5. 🧪 Probar ejemplos: Ejecutar ejemplos rápidos
6. 🚀 Implementar: Migrar código existente

✨ BENEFICIOS:

✓ Soporte para activos peruanos (BVL)
✓ Compatible hacia atrás (código existente sin cambios)
✓ Arquitectura escalable y mantenible
✓ Fácil de agregar nuevas fuentes
✓ Homogenización de datos

⚠️  IMPORTANTE:

- No es necesario cambiar UnifiedPortfolioManager
- DataFetcher mantiene interfaz original
- Código nuevo y antiguo pueden coexistir
- Usar .env para credenciales sensibles

📚 DOCUMENTACIÓN:

- ARCHITECTURE_GUIDE.py: Documentación técnica completa
- Este archivo: Guía de implementación paso a paso
- data_providers.py: Docstrings detallados
- data_fetcher_integration.py: Ejemplos de uso

❓ PREGUNTAS?

Revisar la sección "SOLUCIÓN DE PROBLEMAS" en este archivo.
""")
