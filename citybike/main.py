from datetime import datetime, timedelta

from system import BikeShareSystem
from factories import BikeFactory
from models import Trip
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
    # ============================================================
    # 1️ Analytics
    # ============================================================
    analyzer = DataAnalyzer(output_dir="output")
    analyzer.load_data()
    analyzer._clean_trips()

    distances = analyzer.trips["distance_km"].fillna(
        analyzer.trips["distance_km"].median()
    )
    distances_list = distances.tolist()

    print("\n--- First 5 distances ---")
    print(distances_list[:5])

    # ---- NEW: MAX DISTANCE ----
    max_distance = distances.max()
    print(f"\nMaximum trip distance: {max_distance:.2f} km")
    if max_distance > 24:
        print("⚠️ There are extremely long trips!")
    else:
        print("All trips are shorter than 24 km ✅")

    analyzer.generate_summary_report()

    # ============================================================
    # 2️ System Integration
    # ============================================================
    system = BikeShareSystem()

    print("\n--- Loading data into system ---")
    system.load_from_analyzer(analyzer)

    print(f"Loaded {len(system.users)} users")
    print(f"Loaded {len(system.stations)} stations")

    # ============================================================
    # 3 Factory Pattern Demo
    # ============================================================
    demo_bike = BikeFactory.create_from_dict({
        "bike_id": "DEMO-E001",
        "bike_type": "electric",
        "battery_level": 85.0,
        "max_range_km": 45.0
    })
    system.add_bike(demo_bike)
    print(f"\nCreated demo bike: {demo_bike}")

    # Create demo trip with first user & station
    if system.users and system.stations:
        user = list(system.users.values())[0]
        station = list(system.stations.values())[0]

        print(f"\n--- Creating demo trip for user {user.name} ---")

        trip = Trip(
            "DEMO-TRIP-001",
            user,
            demo_bike,
            station,
            station,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(minutes=25),
            distance_km=3.5
        )

        system.record_trip(trip)
        cost = system.calculate_trip_cost(trip)

        print(f"Trip duration: {trip.duration_minutes} minutes")
        print(f"Trip distance: {trip.distance_km} km")
        print(f"Trip cost: €{cost:.2f}")

    # ============================================================
    # 4 System Summary
    # ============================================================
    print("\n--- System Summary ---")
    print(system)
    print(f"Total trips recorded: {len(system.trips)}")

    # ============================================================
    # 5 Sorting & Searching
    # ===========================================================
    sorted_merge = merge_sort(distances_list)
    sorted_insertion = insertion_sort(distances_list)

    print("\n--- First 10 sorted distances ---")
    print("Merge Sort:", sorted_merge[:10])
    print("Insertion Sort:", sorted_insertion[:10])

    target = distances_list[len(distances_list) // 2]

    idx_binary = binary_search(sorted_merge, target)
    idx_linear = linear_search(distances_list, target)

    print(f"\nBinary search index for {target}: {idx_binary}")
    print(f"Linear search index for {target}: {idx_linear}")

    # ============================================================
    # 6 Benchmarking
    # ============================================================
    print("\n--- Benchmark Results ---")
    print("Sort benchmark (ms):", benchmark_sort(distances_list))
    print("Search benchmark (ms):", benchmark_search(distances_list, target))

    # ============================================================
    # 7 Visualizations
    # ============================================================
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
