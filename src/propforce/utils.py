"""
Utility functions for data handling and validation.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional


def load_uiuc_data(filepath: Path) -> pd.DataFrame:
    """
    Load UIUC propeller database CSV file.
    
    Expected columns: RPM, V (m/s), T (N), Q (N·m), J, CT, CP
    
    Parameters
    ----------
    filepath : Path
        Path to CSV file
        
    Returns
    -------
    df : DataFrame
    """
    df = pd.read_csv(filepath)
    required_cols = ['RPM', 'V', 'T', 'Q']
    
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    return df


def compute_error_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Tuple[float, float, float]:
    """
    Compute RMSE, MAE, and R² for validation.
    
    Parameters
    ----------
    y_true : array
        Ground truth values
    y_pred : array
        Predicted values
        
    Returns
    -------
    rmse : float
    mae : float
    r2 : float
    """
    errors = y_true - y_pred
    rmse = np.sqrt(np.mean(errors**2))
    mae = np.mean(np.abs(errors))
    
    ss_res = np.sum(errors**2)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    r2 = 1 - (ss_res / (ss_tot + 1e-12))
    
    return rmse, mae, r2


def default_loading_coeffs(profile: str = "elliptic") -> np.ndarray:
    """
    Return default loading coefficient profiles.
    
    Parameters
    ----------
    profile : str
        'uniform', 'elliptic', 'linear', 'quadratic'
        
    Returns
    -------
    coeffs : array
    """
    profiles = {
        'uniform': np.array([2.0, 0.0, 0.0, 0.0, 0.0]),
        'linear': np.array([1.0, 2.0, 0.0, 0.0, 0.0]),
        'elliptic': np.array([0.5, 1.0, 3.0, -1.5, 0.0]),
        'quadratic': np.array([1.0, 0.5, 2.0, 0.0, 0.0]),
    }
    
    if profile not in profiles:
        raise ValueError(f"Unknown profile: {profile}. Choose from {list(profiles.keys())}")
    
    return profiles[profile]


def validate_inputs(
    diameter: float,
    rpm: float,
    velocity: float,
) -> None:
    """
    Check physical bounds on inputs.
    
    Raises
    ------
    ValueError if any input is out of reasonable range
    """
    if not (0.05 <= diameter <= 2.0):
        raise ValueError(f"Diameter {diameter} m outside range [0.05, 2.0]")
    
    if not (100 <= rpm <= 20000):
        raise ValueError(f"RPM {rpm} outside range [100, 20000]")
    
    if not (0 <= velocity <= 100):
        raise ValueError(f"Velocity {velocity} m/s outside range [0, 100]")