"""
Test script for numerical.py
Performs checks on:
    - Station distance matrix
    - Trip statistics
    - Outlier detection
    - Vectorized fare calculation - python -m tests.test_numerical
"""

import numpy as np
from pathlib import Path
import sys


sys.path.append(str(Path(__file__).resolve().parent.parent))

from analyzer import DataAnalyzer
from numerical import (
    station_distance_matrix,
    trip_duration_stats,
    detect_outliers_zscore,
    calculate_fares
)

def main():
    # -----------------------------
    # Load data
    # -----------------------------
    analyzer = DataAnalyzer()
    analyzer.load_data()

    print("\n--- First 5 trips ---")
    print(analyzer.trips.head())

    print("\n--- First 5 stations ---")
    print(analyzer.stations.head())

    # -----------------------------
    # Station distance matrix
    # -----------------------------
    latitudes = analyzer.stations["latitude"].to_numpy()
    longitudes = analyzer.stations["longitude"].to_numpy()

    dist_matrix = station_distance_matrix(latitudes, longitudes)
    print(f"\nStation distance matrix (shape={dist_matrix.shape}):")
    print(dist_matrix)

    # -----------------------------
    # Trip statistics
    # -----------------------------
    durations = analyzer.trips["duration_minutes"].to_numpy()
    stats = trip_duration_stats(durations)
    print("\nTrip duration statistics:")
    for k, v in stats.items():
        print(f"{k}: {v:.2f}")

    # -----------------------------
    # Outlier detection
    # -----------------------------
    outliers_duration = detect_outliers_zscore(durations)
    distances = analyzer.trips["distance_km"].to_numpy()
    outliers_distance = detect_outliers_zscore(distances)

    print(f"\nNumber of outlier trips by duration: {np.sum(outliers_duration)}")
    print(f"Number of outlier trips by distance: {np.sum(outliers_distance)}")

    # -----------------------------
    # Vectorized fare calculation
    # -----------------------------
    per_minute = 0.15
    per_km = 0.10
    unlock_fee = 1.0

    fares = calculate_fares(durations, distances, per_minute, per_km, unlock_fee)
    print("\nFirst 10 calculated fares:")
    print(fares[:10])

if __name__ == "__main__":
    main()
