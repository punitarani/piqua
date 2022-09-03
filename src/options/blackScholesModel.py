# Black-Scholes Options Pricing Model

import numpy as np
from scipy.stats import norm


"""
Variables:
    C:  Call option price
    P:  Put option price
    S:  Underlying stock price
    t:  Time to expiration
    K:  Strike price
    r:  Risk-free interest rate
    V:  Volatility

    N:  Normal distribution function
    D: Conditional probabilities
"""


# Call Price
def C(K: float, t: float, S: float, V: float, r: float = 0.02):
    d1, d2 = D(S, K, r, V, t)

    call = np.multiply(S, norm.cdf(d1)) - np.multiply(norm.cdf(d2) * K, np.exp(-r * t))
    return call


# Put Price
def P(K: float, t: float, S: float, V: float, r: float = 0.02):
    d1, d2 = D(S, K, r, V, t)

    call = -np.multiply(S, norm.cdf(-d1)) + np.multiply(norm.cdf(-d2) * K, np.exp(-r * t))
    return call


# Conditional Probability
def D(S: float, K: float, r: float, V: float, t: float):
    d1 = np.multiply(1 / V * np.divide(1, np.sqrt(t)), np.log(S/K) + (r + V**2 / 2) * t)
    d2 = d1 - V * np.sqrt(t)
    return d1, d2
