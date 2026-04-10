import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# ==================== LSTM MODEL ====================

class LSTMPortfolioPredictor:
    """Modelo LSTM para predicción de retornos de portafolio"""
    
    def __init__(self, returns, lookback=20):
        """
        Inicializa el modelo LSTM
        
        Parameters:
        -----------
        returns : pd.DataFrame o pd.Series
            Retornos históricos
        lookback : int
            Ventana de análisis
        """
        self.returns = returns if isinstance(returns, pd.Series) else returns.mean(axis=1)
        self.lookback = lookback
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.history = None
    
    def prepare_data(self):
        """Prepara datos para LSTM"""
        # Escalar datos
        scaled_data = self.scaler.fit_transform(self.returns.values.reshape(-1, 1))
        
        X, y = [], []
        for i in range(self.lookback, len(scaled_data)):
            X.append(scaled_data[i-self.lookback:i, 0])
            y.append(scaled_data[i, 0])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split 80-20
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Reshape para LSTM [samples, time steps, features]
        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
        
        return X_train, X_test, y_train, y_test
    
    def build_model(self):
        """Construye la arquitectura LSTM"""
        self.model = Sequential([
            LSTM(50, activation='relu', input_shape=(self.lookback, 1), return_sequences=True),
            Dropout(0.2),
            LSTM(50, activation='relu'),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dropout(0.1),
            Dense(1)
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
    
    def train(self, epochs=50, batch_size=32, validation_split=0.1):
        """Entrena el modelo LSTM"""
        X_train, X_test, y_train, y_test = self.prepare_data()
        
        self.build_model()
        
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0
        )
        
        # Evaluar
        train_predictions = self.model.predict(X_train, verbose=0)
        test_predictions = self.model.predict(X_test, verbose=0)
        
        train_rmse = np.sqrt(mean_squared_error(y_train, train_predictions))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
        test_r2 = r2_score(y_test, test_predictions)
        test_mae = mean_absolute_error(y_test, test_predictions)
        
        return {
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'test_r2': test_r2,
            'test_mae': test_mae,
            'train_predictions': train_predictions,
            'test_predictions': test_predictions,
            'y_train': y_train,
            'y_test': y_test
        }
    
    def predict_future(self, days=30):
        """Predice retornos futuros"""
        predictions = []
        
        # Usar últimos lookback días como entrada
        last_data = self.scaler.transform(self.returns.tail(self.lookback).values.reshape(-1, 1))
        current_batch = last_data.reshape((1, self.lookback, 1))
        
        for _ in range(days):
            current_pred = self.model.predict(current_batch, verbose=0)[0, 0]
            predictions.append(current_pred)
            
            # Actualizar batch
            current_batch = np.append(current_batch[:, 1:, :], 
                                     [[[current_pred]]], axis=1)
        
        # Invertir escala
        predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        
        return predictions.flatten()
    
    def plot_training_history(self):
        """Gráfica del historial de entrenamiento"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        axes[0].plot(self.history.history['loss'], label='Training Loss')
        axes[0].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[0].set_title('Model Loss')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        
        axes[1].plot(self.history.history['mae'], label='Training MAE')
        axes[1].plot(self.history.history['val_mae'], label='Validation MAE')
        axes[1].set_title('Model MAE')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('MAE')
        axes[1].legend()
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        return fig


# ==================== GRADIENT BOOSTING MODEL ====================

class GBPortfolioPredictor:
    """Modelo Gradient Boosting para predicción"""
    
    def __init__(self, returns, lookback=20):
        self.returns = returns if isinstance(returns, pd.Series) else returns.mean(axis=1)
        self.lookback = lookback
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
    
    def prepare_data(self):
        """Prepara datos"""
        X, y = [], []
        for i in range(self.lookback, len(self.returns)):
            X.append(self.returns.iloc[i-self.lookback:i].values)
            y.append(self.returns.iloc[i])
        
        X = np.array(X)
        y = np.array(y)
        
        split = int(len(X) * 0.8)
        return X[:split], X[split:], y[:split], y[split:]
    
    def train(self):
        """Entrena el modelo"""
        X_train, X_test, y_train, y_test = self.prepare_data()
        
        self.model.fit(X_train, y_train)
        
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        return {
            'train_r2': r2_score(y_train, train_pred),
            'test_r2': r2_score(y_test, test_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
            'test_mae': mean_absolute_error(y_test, test_pred)
        }
    
    def predict_future(self, days=30):
        """Predice retornos futuros"""
        last_data = self.returns.tail(self.lookback).values
        predictions = []
        
        for _ in range(days):
            next_pred = self.model.predict([last_data])[0]
            predictions.append(next_pred)
            last_data = np.append(last_data[1:], next_pred)
        
        return np.array(predictions)


# ==================== ENSEMBLE MODEL ====================

class EnsemblePortfolioPredictor:
    """Modelo Ensemble que combina múltiples predicciones"""
    
    def __init__(self, returns, lookback=20):
        self.returns = returns if isinstance(returns, pd.Series) else returns.mean(axis=1)
        self.lookback = lookback
        self.lstm = LSTMPortfolioPredictor(returns, lookback)
        self.gb = GBPortfolioPredictor(returns, lookback)
        self.rf = RandomForestRegressor(n_estimators=100, random_state=42)
    
    def train(self):
        """Entrena todos los modelos"""
        lstm_results = self.lstm.train()
        gb_results = self.gb.train()
        
        # Entrenar Random Forest
        X_train, X_test, y_train, y_test = self.gb.prepare_data()
        self.rf.fit(X_train, y_train)
        rf_pred = self.rf.predict(X_test)
        
        return {
            'lstm': lstm_results,
            'gb': gb_results,
            'rf': {
                'r2': r2_score(y_test, rf_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, rf_pred)),
                'mae': mean_absolute_error(y_test, rf_pred)
            }
        }
    
    def predict_future(self, days=30):
        """Promedia predicciones de los 3 modelos"""
        lstm_pred = self.lstm.predict_future(days)
        gb_pred = self.gb.predict_future(days)
        rf_pred = self.rf.predict(
            np.array([self.returns.tail(self.lookback).values] * days)
        )
        
        ensemble_pred = (lstm_pred.flatten() + gb_pred + rf_pred) / 3
        
        return {
            'lstm': lstm_pred.flatten(),
            'gb': gb_pred,
            'rf': rf_pred,
            'ensemble': ensemble_pred
        }
    
    def plot_comparison(self, days=30):
        """Compara predicciones de los 3 modelos"""
        predictions = self.predict_future(days)
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(range(days), predictions['lstm'], marker='o', label='LSTM', linewidth=2)
        ax.plot(range(days), predictions['gb'], marker='s', label='Gradient Boosting', linewidth=2)
        ax.plot(range(days), predictions['rf'], marker='^', label='Random Forest', linewidth=2)
        ax.plot(range(days), predictions['ensemble'], marker='*', label='Ensemble', 
               linewidth=3, color='black', linestyle='--')
        
        ax.set_title('Comparación de Predicciones - Ensemble de Modelos')
        ax.set_xlabel('Días')
        ax.set_ylabel('Retorno Predicho')
        ax.legend()
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        return fig


# ==================== EJEMPLO DE USO ====================

if __name__ == "__main__":
    import yfinance as yf
    from datetime import datetime, timedelta
    
    print("="*80)
    print("🤖 MODELOS AVANZADOS DE MACHINE LEARNING PARA PORTAFOLIO")
    print("="*80)
    
    # Descargar datos
    print("\n📥 Descargando datos...")
    prices = yf.download(['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
                         start=(datetime.now() - timedelta(days=365)),
                         end=datetime.now(),
                         progress=False)['Adj Close']
    
    returns = prices.pct_change().dropna()
    portfolio_returns = returns.mean(axis=1)
    
    # 1. LSTM
    print("\n🔷 Entrenando LSTM...")
    lstm = LSTMPortfolioPredictor(portfolio_returns, lookback=20)
    lstm_results = lstm.train(epochs=50)
    print(f"   LSTM Test R²: {lstm_results['test_r2']:.4f}")
    print(f"   LSTM Test RMSE: {lstm_results['test_rmse']:.6f}")
    
    # 2. Gradient Boosting
    print("\n🔶 Entrenando Gradient Boosting...")
    gb = GBPortfolioPredictor(portfolio_returns, lookback=20)
    gb_results = gb.train()
    print(f"   GB Test R²: {gb_results['test_r2']:.4f}")
    print(f"   GB Test RMSE: {gb_results['test_rmse']:.6f}")
    
    # 3. Ensemble
    print("\n🔷🔶 Entrenando Ensemble...")
    ensemble = EnsemblePortfolioPredictor(portfolio_returns, lookback=20)
    ensemble_results = ensemble.train()
    
    # Predicciones
    print("\n🎯 Realizando predicciones para 30 días...")
    predictions = ensemble.predict_future(days=30)
    
    print(f"\nPredicciones de Ensemble (primeros 5 días):")
    print(predictions['ensemble'][:5])
    
    print("\n✅ Modelos entrenados exitosamente!")
    print("="*80)
