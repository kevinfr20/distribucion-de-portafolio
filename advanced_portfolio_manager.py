import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from scipy.stats import norm

class AdvancedPortfolioManager:
    def __init__(self, tickers, start_date):
        self.tickers = tickers
        self.start_date = start_date
        self.data = self.download_data()

    def download_data(self):
        return yf.download(self.tickers, start=self.start_date)['Adj Close']

    def monte_carlo_simulation(self, num_simulations=5000):
        daily_returns = self.data.pct_change().dropna()
        mean_return = daily_returns.mean()
        cov_matrix = daily_returns.cov()
        results = np.zeros((num_simulations, len(self.tickers)))
        for i in range(num_simulations):
            weights = np.random.random(len(self.tickers))
            weights /= np.sum(weights)
            portfolio_return = np.dot(weights, mean_return) * 252
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
            results[i] = [portfolio_return, portfolio_volatility]
        return results

    def stress_testing(self):
        crises = [-0.05, -0.15, 0.10, 0.20]
        results = {} 
        for crisis in crises:
            results[crisis] = self.data.pct_change().mean() + crisis
        return results

    def backtesting(self, starting_value=10000):
        portfolio_value = [starting_value]
        for date, row in self.data.iterrows():
            returns = row.pct_change().dropna()
            portfolio_value.append(portfolio_value[-1] * (1 + returns.mean()))
        return portfolio_value

    def sensitivity_analysis(self):
        heatmap_data = np.random.rand(10, 10)  # Example heatmap data
        sns.heatmap(heatmap_data)
        plt.title('Sensitivity Analysis Heatmap')
        plt.show()

    def visualize_simulations(self, simulations):
        plt.figure(figsize=(10, 6))
        plt.title('Monte Carlo Simulations')
        plt.xlabel('Simulation Number')
        plt.ylabel('Portfolio Return')
        plt.plot(simulations[:, 0])
        plt.show()

    def run(self):
        # Running all features
        simulations = self.monte_carlo_simulation()
        stress_results = self.stress_testing()
        backtest_performance = self.backtesting()
        self.visualize_simulations(simulations)
        self.sensitivity_analysis()


if __name__ == '__main__':
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    start_date = '2023-01-01'
    apm = AdvancedPortfolioManager(tickers, start_date)
    apm.run()