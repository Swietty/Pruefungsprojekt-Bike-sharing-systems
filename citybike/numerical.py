"""
NumPy-based numerical computations for the CityBike platform.

This module provides:
    - Pairwise station distance calculations
    - Vectorized trip duration statistics
    - Outlier detection using z-scores
    - Vectorized fare calculation

All functions operate purely on NumPy arrays.
"""

import numpy as np



# Station distance matrix

def station_distance_matrix(
    latitudes: np.ndarray,
    longitudes: np.ndarray,
) -> np.ndarray:
    """Compute pairwise Euclidean distances between stations.

    Uses a simplified flat-earth model:
        d = sqrt((lat2 - lat1)^2 + (lon2 - lon1)^2)

    Args:
        latitudes: 1-D array of station latitudes.
        longitudes: 1-D array of station longitudes.

    Returns:
        2-D symmetric distance matrix of shape (n, n).
    """
    lat_diff = latitudes[:, np.newaxis] - latitudes[np.newaxis, :]
    lon_diff = longitudes[:, np.newaxis] - longitudes[np.newaxis, :]

    return np.sqrt(lat_diff ** 2 + lon_diff ** 2)


# ---------------------------------------------------------------------------
# Trip statistics
# ---------------------------------------------------------------------------

def trip_duration_stats(durations: np.ndarray) -> dict[str, float]:
    """Compute summary statistics for trip durations.

    NaN values are ignored.

    Args:
        durations: 1-D array of trip durations in minutes.

    Returns:
        Dictionary with mean, median, std, p25, p75, p90.
    """
    durations = durations[~np.isnan(durations)]

    if durations.size == 0:
        return {
            "mean": np.nan,
            "median": np.nan,
            "std": np.nan,
            "p25": np.nan,
            "p75": np.nan,
            "p90": np.nan,
        }

    return {
        "mean": float(np.mean(durations)),
        "median": float(np.median(durations)),
        "std": float(np.std(durations)),
        "p25": float(np.percentile(durations, 25)),
        "p75": float(np.percentile(durations, 75)),
        "p90": float(np.percentile(durations, 90)),
    }


# ---------------------------------------------------------------------------
# Outlier detection
# ---------------------------------------------------------------------------

def detect_outliers_zscore(
    values: np.ndarray,
    threshold: float = 3.0,
) -> np.ndarray:
    """Detect outliers using the z-score method.

    An observation is considered an outlier if |z| > threshold.

    NaN values are ignored and never marked as outliers.

    Args:
        values: 1-D array of numeric values.
        threshold: Z-score cutoff (default 3.0).

    Returns:
        Boolean array where True indicates an outlier.
    """
    mask = ~np.isnan(values)
    clean_values = values[mask]

    if clean_values.size == 0:
        return np.zeros_like(values, dtype=bool)

    mean = np.mean(clean_values)
    std = np.std(clean_values)

    if std == 0:
        return np.zeros_like(values, dtype=bool)

    z_scores = (clean_values - mean) / std
    outliers_clean = np.abs(z_scores) > threshold

    outliers = np.zeros_like(values, dtype=bool)
    outliers[mask] = outliers_clean

    return outliers


# ---------------------------------------------------------------------------
# Vectorized fare calculation
# ---------------------------------------------------------------------------

def calculate_fares(
    durations: np.ndarray,
    distances: np.ndarray,
    per_minute: float,
    per_km: float,
    unlock_fee: float = 0.0,
) -> np.ndarray:
    """Calculate fares for many trips at once using NumPy.

    Args:
        durations: 1-D array of trip durations (minutes).
        distances: 1-D array of trip distances (km).
        per_minute: Cost per minute.
        per_km: Cost per km.
        unlock_fee: Flat unlock fee.

    Returns:
        1-D array of trip fares.
    """
    return unlock_fee + per_minute * durations + per_km * distances
