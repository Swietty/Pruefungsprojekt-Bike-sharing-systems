from datetime import datetime, timedelta
import pandas as pd

from system import BikeShareSystem
from factories import BikeFactory, UserFactory
from models import Station, Trip
from pricing import CasualPricing
from analyzer import DataAnalyzer
from algorithms import (
    merge_sort,
    insertion_sort,
    binary_search,
    linear_search,
    benchmark_sort,
    benchmark_search
)


def main():
    # ---------------------------
    # Analytics 
    # ---------------------------
    analyzer = DataAnalyzer(output_dir="output")  
    analyzer.load_data()
    analyzer._clean_trips() 

    distances = analyzer.trips["distance_km"].fillna(analyzer.trips["distance_km"].median())
    distances_list = distances.tolist()

    print("\n--- First 5 distances ---")
    print(distances_list[:5])

    # Generate final summary report 
    analyzer.generate_summary_report()
    
    # ---------------------------
    # BikeShareSystem 
    # ---------------------------
    system = BikeShareSystem()

    bike = BikeFactory.create_from_dict({
        "bike_id": "B001",
        "bike_type": "classic"
    })

    user = UserFactory.create_from_dict({
        "user_id": "U001",
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "user_type": "casual"
    })

    station = Station("S001", "Central Station", 10)

    system.add_bike(bike)
    system.add_user(user)
    system.add_station(station)

    trip = Trip(
        "T001",
        user,
        bike,
        station,
        station,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=30),
        distance_km=2.5
    )

    system.record_trip(trip)
    system.set_pricing_strategy(CasualPricing())
    cost = system.calculate_trip_cost(trip)

    print(f"\nTrip cost: €{cost:.2f}")
    print(system)

    # ---------------------------
    # Sorting & Searching 
    # ---------------------------
    distances_list = analyzer.trips["distance_km"].fillna(analyzer.trips["distance_km"].median()).tolist()

    sorted_merge = merge_sort(distances_list)
    sorted_insertion = insertion_sort(distances_list)

    print("\n--- First 10 distances ---")
    print("Merge Sort:", sorted_merge[:10])
    print("Insertion Sort:", sorted_insertion[:10])

    target_distance = distances_list[len(distances_list)//2]  
    idx_binary = binary_search(sorted_merge, target_distance)
    idx_linear = linear_search(distances_list, target_distance)

    print(f"\nBinary search index for {target_distance}: {idx_binary}")
    print(f"Linear search index for {target_distance}: {idx_linear}")

    # ---------------------------
    # Benchmarking
    # ---------------------------
    print("\nSort benchmark (ms):", benchmark_sort(distances_list))
    print("Search benchmark (ms):", benchmark_search(distances_list, target_distance))

    # ---------------------------
    # Visualizations
    # ---------------------------
    from visualization import (
        plot_trips_per_station,
        plot_monthly_trend,
        plot_duration_histogram,
        plot_duration_by_user_type
    )

    plot_trips_per_station(analyzer.trips, analyzer.stations)
    plot_monthly_trend(analyzer.trips)
    plot_duration_histogram(analyzer.trips)
    plot_duration_by_user_type(analyzer.trips)


if __name__ == "__main__":
    main()
