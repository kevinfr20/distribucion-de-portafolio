"""
Módulo: test_bvl_provider.py
Descripción: Suite de pruebas unitarias para BVLDataProvider y LocalCSVProvider.
Autor: Software Engineer
Fecha: 2026-05-19
"""

import logging
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pandas as pd

# Importar los módulos a probar
# Nota: Ajustar las rutas según la estructura del proyecto
from data_providers.base_provider import BaseDataProvider
from data_providers.local_csv_provider import LocalCSVProvider
from data_providers.bvl_data_provider import BVLDataProvider

# Silenciar logs durante las pruebas
logging.disable(logging.CRITICAL)


class TestLocalCSVProvider(unittest.TestCase):
    """
    Suite de pruebas para LocalCSVProvider.
    """

    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.fallback_dir = "./test_data/bvl_fallback/"
        self.provider = LocalCSVProvider(
            fallback_dir=self.fallback_dir,
            encoding="utf-8",
            delimiter=";",
        )

    def test_init_creates_directory(self):
        """Verifica que el inicializador crea el directorio."""
        self.assertTrue(Path(self.fallback_dir).exists())

    def test_get_csv_path(self):
        """Verifica que se construye correctamente la ruta del CSV."""
        csv_path = self.provider.get_csv_path("ALICORC1")
        expected = Path(self.fallback_dir) / "ALICORC1.csv"
        self.assertEqual(csv_path, expected)

    def test_get_csv_path_uppercase(self):
        """Verifica que el ticker se convierte a mayúsculas."""
        csv_path = self.provider.get_csv_path("alicorc1")
        expected = Path(self.fallback_dir) / "ALICORC1.csv"
        self.assertEqual(csv_path, expected)

    def test_file_exists_nonexistent(self):
        """Verifica que retorna False para archivo inexistente."""
        self.assertFalse(self.provider.file_exists("NONEXISTENT123"))

    def test_standardize_columns(self):
        """Verifica que estandariza correctamente los nombres de columnas."""
        # Crear DataFrame con nombres de columnas de BVL
        df = pd.DataFrame({
            "Fecha de cotización": ["15/05/2026"],
            "Apertura": [1.69],
            "Máximo": [1.69],
            "Mínimo": [1.68],
            "Cierre": [1.68],
            "Cantidad negociada": [19052],
        })

        result = self.provider._standardize_columns(df)

        # Verificar nombres de columnas
        expected_cols = ["Open", "High", "Low", "Close", "Volume"]
        self.assertListEqual(list(result.columns), expected_cols)

        # Verificar que Date es índice
        self.assertIsInstance(result.index, pd.DatetimeIndex)

    def test_standardize_columns_missing_column(self):
        """Verifica que lanza excepción si faltan columnas."""
        df = pd.DataFrame({
            "Fecha de cotización": ["15/05/2026"],
            "Apertura": [1.69],
            # Faltan otras columnas
        })

        with self.assertRaises(ValueError) as context:
            self.provider._standardize_columns(df)

        self.assertIn("Columnas faltantes", str(context.exception))

    def test_standardize_dtypes(self):
        """Verifica que estandariza correctamente los tipos de datos."""
        df = pd.DataFrame({
            "Date": pd.date_range("2025-01-01", periods=3),
            "Open": ["1,69", "1,70", "1,71"],
            "High": ["1,70", "1,71", "1,72"],
            "Low": ["1,68", "1,69", "1,70"],
            "Close": ["1,68", "1,70", "1,71"],
            "Volume": ["19052", "20000", "25000"],
        })
        df.set_index("Date", inplace=True)

        result = self.provider._standardize_dtypes(df)

        # Verificar tipos de datos
        for col in ["Open", "High", "Low", "Close"]:
            self.assertIn(str(result[col].dtype), ["float64", "float32"])
        
        self.assertEqual(str(result["Volume"].dtype), "int64")

    def test_create_empty_dataframe(self):
        """Verifica que crea un DataFrame vacío con estructura correcta."""
        df = self.provider._create_empty_dataframe()

        self.assertTrue(df.empty)
        self.assertListEqual(list(df.columns), ["Open", "High", "Low", "Close", "Volume"])
        self.assertIsInstance(df.index, pd.DatetimeIndex)


class TestBVLDataProvider(unittest.TestCase):
    """
    Suite de pruebas para BVLDataProvider.
    """

    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.provider = BVLDataProvider(
            api_base_url="https://api.bvl.com.pe/v1",
            api_timeout=30,
            fallback_dir="./test_data/bvl_fallback/",
        )

    def test_init(self):
        """Verifica inicialización correcta."""
        self.assertEqual(self.provider.api_base_url, "https://api.bvl.com.pe/v1")
        self.assertEqual(self.provider.api_timeout, 30)
        self.assertIsNotNone(self.provider.csv_provider)

    def test_required_columns(self):
        """Verifica que se definen las columnas requeridas."""
        expected = ["Date", "Open", "High", "Low", "Close", "Volume"]
        self.assertListEqual(self.provider.required_columns, expected)

    def test_validate_data_valid(self):
        """Verifica que valida correctamente un DataFrame válido."""
        df = pd.DataFrame({
            "Open": [1.69, 1.70],
            "High": [1.70, 1.71],
            "Low": [1.68, 1.69],
            "Close": [1.68, 1.70],
            "Volume": [19052, 20000],
        }, index=pd.date_range("2025-01-01", periods=2))

        # No debe lanzar excepción
        is_valid = self.provider.validate_data(df, "ALICORC1")
        self.assertTrue(is_valid)

    def test_validate_data_empty(self):
        """Verifica que lanza excepción para DataFrame vacío."""
        df = pd.DataFrame()

        with self.assertRaises(ValueError):
            self.provider.validate_data(df, "ALICORC1")

    def test_validate_data_missing_column(self):
        """Verifica que lanza excepción si faltan columnas."""
        df = pd.DataFrame({
            "Open": [1.69],
            "High": [1.70],
            # Faltan otras columnas
        }, index=pd.date_range("2025-01-01", periods=1))

        with self.assertRaises(ValueError) as context:
            self.provider.validate_data(df, "ALICORC1")

        self.assertIn("Columnas faltantes", str(context.exception))

    def test_validate_data_invalid_index(self):
        """Verifica que lanza excepción si el índice no es DatetimeIndex."""
        df = pd.DataFrame({
            "Open": [1.69],
            "High": [1.70],
            "Low": [1.68],
            "Close": [1.68],
            "Volume": [19052],
        })

        with self.assertRaises(ValueError) as context:
            self.provider.validate_data(df, "ALICORC1")

        self.assertIn("DatetimeIndex", str(context.exception))

    @patch('data_providers.bvl_data_provider.requests.get')
    def test_fetch_from_api_timeout(self, mock_get):
        """Verifica que maneja correctamente el timeout de la API."""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()

        with self.assertRaises(TimeoutError):
            self.provider._fetch_from_api(
                ticker="ALICORC1",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 12, 31),
            )

    @patch('data_providers.bvl_data_provider.requests.get')
    def test_fetch_from_api_connection_error(self, mock_get):
        """Verifica que maneja correctamente errores de conexión."""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError()

        with self.assertRaises(ConnectionError):
            self.provider._fetch_from_api(
                ticker="ALICORC1",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 12, 31),
            )

    def test_get_historical_data_fallback_to_csv(self):
        """Verifica que intenta fallback a CSV cuando la API falla."""
        # Mock de la API para fallar
        with patch.object(self.provider, '_fetch_from_api', side_effect=ConnectionError()):
            # Mock de LocalCSVProvider para retornar datos válidos
            mock_df = pd.DataFrame({
                "Open": [1.69],
                "High": [1.70],
                "Low": [1.68],
                "Close": [1.68],
                "Volume": [19052],
            }, index=pd.date_range("2025-01-01", periods=1))

            with patch.object(self.provider.csv_provider, 'load_historical_data', return_value=mock_df):
                result = self.provider.get_historical_data(
                    ticker="ALICORC1",
                    start_date=datetime(2025, 1, 1),
                    end_date=datetime(2025, 1, 31),
                )

                # Verificar que se retornaron datos
                self.assertIsNotNone(result)
                self.assertEqual(len(result), 1)

    def test_get_historical_data_api_and_csv_fail(self):
        """Verifica que lanza excepción cuando API y CSV fallan."""
        # Mock ambos para fallar
        with patch.object(self.provider, '_fetch_from_api', side_effect=ConnectionError()):
            with patch.object(self.provider.csv_provider, 'load_historical_data', side_effect=FileNotFoundError()):
                with self.assertRaises(ValueError) as context:
                    self.provider.get_historical_data(
                        ticker="ALICORC1",
                        start_date=datetime(2025, 1, 1),
                        end_date=datetime(2025, 1, 31),
                    )

                error_msg = str(context.exception)
                self.assertIn("No se pudo obtener data", error_msg)
                self.assertIn("ALICORC1", error_msg)


class TestIntegration(unittest.TestCase):
    """
    Suite de pruebas de integración.
    """

    def test_full_workflow_csv_fallback(self):
        """Verifica el flujo completo: API falla -> CSV carga datos."""
        provider = BVLDataProvider(
            api_base_url="https://api.invalid.com",
            api_timeout=5,
            fallback_dir="./test_data/bvl_fallback/",
        )

        # Crear archivo CSV de prueba
        csv_dir = Path(provider.csv_provider.fallback_dir)
        csv_dir.mkdir(parents=True, exist_ok=True)

        test_csv = csv_dir / "TESTICKER.csv"
        
        # Crear CSV con formato de BVL
        test_data = """Fecha de cotización;Apertura;Cierre;Máximo;Mínimo;Promedio;Cantidad negociada;Monto negociado (S/);Fecha anterior;Cierre anterior corregido
15/05/2026;1.69;1.68;1.69;1.68;1.6952902582406046;19052;32298.67;14/05/2026;1.72
14/05/2026;1.72;1.72;1.72;1.72;1.7241912287633345;12655;21819.64;13/05/2026;1.702
"""
        test_csv.write_text(test_data, encoding="utf-8")

        try:
            # Esto debería fallar en API e intentar CSV
            with patch.object(provider, '_fetch_from_api', side_effect=ConnectionError()):
                df = provider.get_historical_data(
                    ticker="TESTICKER",
                    start_date=datetime(2026, 5, 1),
                    end_date=datetime(2026, 5, 31),
                )

                # Verificar que obtuvo datos
                self.assertIsNotNone(df)
                self.assertGreater(len(df), 0)
                self.assertListEqual(
                    list(df.columns),
                    ["Open", "High", "Low", "Close", "Volume"]
                )

        finally:
            # Limpiar
            if test_csv.exists():
                test_csv.unlink()


if __name__ == "__main__":
    # Ejecutar todas las pruebas
    unittest.main(verbosity=2)
