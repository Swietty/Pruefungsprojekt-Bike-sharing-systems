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
    # BikeShareSystem Integration
    # ---------------------------
    system = BikeShareSystem()
    
    # loading data from analyzer into system
    print("\n--- Loading data from analyzer into system ---")
    system.load_from_analyzer(analyzer)
    print(f" Loaded {len(system.users)} users and {len(system.stations)} stations from CSV")
    
    #  Factory Pattern Demonstration
    print("\n--- Factory Pattern Demonstration ---")
    demo_bike = BikeFactory.create_from_dict({
        "bike_id": "DEMO-E001",
        "bike_type": "electric",
        "battery_level": 85.0,
        "max_range_km": 45.0
    })
    print(f" Created demo bike: {demo_bike}")
    system.add_bike(demo_bike)
    
    # use real user from CSV to create a trip
    if system.users:
        # select first user from the loaded users
        first_user = list(system.users.values())[0]
        print(f"\n--- Creating test trip with real user from CSV ---")
        print(f"Using user: {first_user.name} ({first_user.id})")
        
        # select first station from the loaded stations
        first_station = list(system.stations.values())[0] if system.stations else None
        
        if first_station:
            # create a test trip
            test_trip = Trip(
                "DEMO-TRIP-001",
                first_user,
                demo_bike,
                first_station,
                first_station,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(minutes=25),
                distance_km=3.5
            )
            
            # record the trip in the system
            system.record_trip(test_trip)
            
            # calculate cost using the pricing strategy
            system.set_pricing_strategy(CasualPricing())
            cost = system.calculate_trip_cost(test_trip)
            
            print(f" Trip created: {test_trip.duration_minutes} min, {test_trip.distance_km} km")
            print(f" Trip cost: €{cost:.2f} (CasualPricing strategy)")
    
    # final summary of the system state
    print(f"\n {system}")
    print(f"   Total trips recorded: {len(system.trips)}")
    print(f"   Pricing strategy: {system.pricing_strategy.get_name()}")
    

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
