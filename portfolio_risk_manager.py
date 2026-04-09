import numpy as np
import pandas as pd

class PortfolioRiskManager:
    def __init__(self, returns):
        self.returns = returns

    def calculate_volatility(self):
        """Calculate the annualized volatility of the portfolio."""
        return np.std(self.returns) * np.sqrt(252)

    def correlation_matrix(self):
        """Calculate the correlation matrix of asset returns."""
        return self.returns.corr()

    def value_at_risk(self, confidence_level=0.95):
        """Calculate the Value at Risk (VaR)."""
        return -np.percentile(self.returns, 100 * (1 - confidence_level))

    def sharpe_ratio(self, risk_free_rate=0.01):
        """Calculate the Sharpe Ratio."""
        excess_return = np.mean(self.returns) - risk_free_rate
        return excess_return / self.calculate_volatility()

    def optimize_portfolio(self, num_portfolios=10000):
        """Optimize portfolio to find the best weight combination."""
        results = []
        for _ in range(num_portfolios):
            weights = np.random.random(len(self.returns.columns))
            weights /= np.sum(weights) 
            returns = np.sum(weights * self.returns.mean()) * 252
            volatility = np.sqrt(np.dot(weights.T, np.dot(self.returns.cov() * 252, weights)))
            sharpe = (returns - 0.01) / volatility  # Assuming risk-free rate is 1%
            results.append((returns, volatility, sharpe, weights))

        return max(results, key=lambda x: x[2])  # Return the portfolio with the highest Sharpe ratio

# Example Usage
# returns = pd.DataFrame({
#     'Asset1': np.random.normal(0.01, 0.02, 252),
#     'Asset2': np.random.normal(0.012, 0.03, 252),
# })
# manager = PortfolioRiskManager(returns)
# print(manager.calculate_volatility())
# print(manager.correlation_matrix())
# print(manager.value_at_risk())
# print(manager.sharpe_ratio())
# print(manager.optimize_portfolio())
