def get_historical_data(ticker, start_date, end_date):
    try:
        # 1️⃣ Intenta obtener de la API
        data = self._fetch_from_api(...)
        if data is not None and not data.empty:
            return data
    except (ConnectionError, TimeoutError, ValueError):
        logger.warning(f"Error en API para {ticker}")
    
    # 2️⃣ Si API falla, intenta CSV
    try:
        data = self.csv_provider.load_historical_data(...)
        if data is not None and not data.empty:
            return data
    except FileNotFoundError:
        logger.error(f"CSV no encontrado para {ticker}")
    
    # 3️⃣ Si ambas fallan, lanza excepción clara
    raise ValueError(
        f"No se pudo obtener data de la API ni del respaldo CSV local "
        f"para el ticker {ticker}"
    )
