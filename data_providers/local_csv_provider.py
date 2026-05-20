
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)

class LocalCSVProvider:
    def __init__(self, fallback_dir: str):
        self.fallback_dir = Path(fallback_dir)
        self.fallback_dir.mkdir(parents=True, exist_ok=True)

    def get_historical_data(self, ticker: str, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        file_path = self.fallback_dir / f"{ticker}.csv"
        if not file_path.exists():
            logger.warning(f"Archivo CSV de respaldo no encontrado para {ticker} en {file_path}.")
            return None

        try:
            # Read CSV - semicolon is common in BVL exports
            df = pd.read_csv(file_path, sep=';', engine='python')

            # Normalize column names
            df.columns = [c.strip() for c in df.columns]
            cols_lower = [c.lower() for c in df.columns]

            # Detect date column (fecha or date)
            date_idx = next((i for i, c in enumerate(cols_lower) if 'fecha' in c or 'date' in c), None)
            if date_idx is None:
                logger.error(f"No se encontró columna de fecha en {file_path}. Columnas: {df.columns.tolist()}")
                return None

            date_col = df.columns[date_idx]
            df['date_internal'] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['date_internal'])
            df.set_index('date_internal', inplace=True)
            df = df.sort_index()

            # Ensure naive timestamps for merging
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)

            # Filter range
            df = df.loc[start_date:end_date]

            # Detect price column (cierre, close, adj, or first numeric)
            price_idx = next((i for i, c in enumerate(cols_lower) if any(x in c for x in ['cierre', 'adj', 'close', 'ultimo'])), None)
            if price_idx is not None:
                price_col = df.columns[price_idx]
                if df[price_col].dtype == object:
                    df['Close'] = pd.to_numeric(df[price_col].astype(str).str.replace(',', '.'), errors='coerce')
                else:
                    df['Close'] = df[price_col]
            else:
                df['Close'] = df.select_dtypes(include=['number']).iloc[:, 0]

            return df[['Close']].dropna()
        except Exception as e:
            logger.error(f"Error al procesar CSV {file_path}: {e}")
            return None
