# qaai_system/utils/noise_injector.py
"""
Noise Injector Utilities (Phase 1.5)

Used for robustness testing of strategies by perturbing OHLCV data.

Supported noise models:
 - Gaussian (normal) noise
 - Uniform noise
 - Jump noise (rare big spikes/drops)
"""

import numpy as np
import pandas as pd


def add_gaussian_noise(
    df: pd.DataFrame, sigma: float = 0.01, seed: int = None
) -> pd.DataFrame:
    """
    Add Gaussian noise to OHLCV prices.

    Args:
        df: OHLCV DataFrame (must have 'open','high','low','close')
        sigma: relative noise std deviation (1% default)
        seed: random seed for reproducibility
    Returns:
        Noisy DataFrame (copy)
    """
    rng = np.random.default_rng(seed)
    noisy = df.copy()
    for col in ["open", "high", "low", "close"]:
        if col in noisy.columns:
            noise = rng.normal(0, sigma, len(noisy))
            noisy[col] = noisy[col] * (1 + noise)
    return noisy


def add_uniform_noise(
    df: pd.DataFrame, level: float = 0.01, seed: int = None
) -> pd.DataFrame:
    """
    Add Uniform noise to OHLCV prices.

    Args:
        df: OHLCV DataFrame
        level: max relative perturbation (±1% default)
        seed: random seed
    Returns:
        Noisy DataFrame (copy)
    """
    rng = np.random.default_rng(seed)
    noisy = df.copy()
    for col in ["open", "high", "low", "close"]:
        if col in noisy.columns:
            noise = rng.uniform(-level, level, len(noisy))
            noisy[col] = noisy[col] * (1 + noise)
    return noisy


def add_jump_noise(
    df: pd.DataFrame, prob: float = 0.01, magnitude: float = 0.05, seed: int = None
) -> pd.DataFrame:
    """
    Inject rare jump noise into OHLCV prices.

    Args:
        df: OHLCV DataFrame
        prob: probability per row of a jump (default 1%)
        magnitude: jump size (±5% default)
        seed: random seed
    Returns:
        Noisy DataFrame (copy)
    """
    rng = np.random.default_rng(seed)
    noisy = df.copy()
    jumps = rng.random(len(noisy)) < prob
    for col in ["open", "high", "low", "close"]:
        if col in noisy.columns:
            factors = np.ones(len(noisy))
            factors[jumps] = 1 + rng.choice([-1, 1], jumps.sum()) * magnitude
            noisy[col] = noisy[col] * factors
    return noisy


def apply_noise(df: pd.DataFrame, model: str = "gaussian", **kwargs) -> pd.DataFrame:
    """
    Apply chosen noise model.

    Args:
        df: OHLCV DataFrame
        model: one of {"gaussian","uniform","jump"}
        kwargs: parameters passed to noise function
    Returns:
        Noisy DataFrame
    """
    if model == "gaussian":
        return add_gaussian_noise(df, **kwargs)
    elif model == "uniform":
        return add_uniform_noise(df, **kwargs)
    elif model == "jump":
        return add_jump_noise(df, **kwargs)
    else:
        raise ValueError(f"Unknown noise model '{model}'")
