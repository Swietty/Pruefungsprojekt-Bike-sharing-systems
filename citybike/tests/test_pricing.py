from datetime import datetime, timedelta
from system import BikeShareSystem
from factories import BikeFactory
from models import Trip, UserType
from analyzer import DataAnalyzer

def test_pricing_combinations():
    # ------------------------------------------------------------
    # Setup system and demo bike -  python -m tests.test_pricing
    # ------------------------------------------------------------
    analyzer = DataAnalyzer(output_dir="output")
    analyzer.load_data()
    analyzer._clean_trips()

    system = BikeShareSystem()
    system.load_from_analyzer(analyzer)

    demo_bike = BikeFactory.create_from_dict({
        "bike_id": "DEMO-E001",
        "bike_type": "electric",
        "battery_level": 85.0,
        "max_range_km": 45.0
    })
    system.add_bike(demo_bike)

    if not system.stations:
        print("No stations available for testing!")
        return

    station = list(system.stations.values())[0]

    # ------------------------------------------------------------
    # Select one MEMBER and one CASUAL user
    # ------------------------------------------------------------
    member_user = next((u for u in system.users.values() if u.user_type == UserType.MEMBER), None)
    casual_user = next((u for u in system.users.values() if u.user_type == UserType.CASUAL), None)

    if not member_user or not casual_user:
        print("Not enough users of each type for testing!")
        return

    # ------------------------------------------------------------
    # Test combinations
    # ------------------------------------------------------------
    print("\n=== Pricing Combination Test ===")
    test_cases = [
        ("MEMBER Normal hour", member_user, 14),  # 14:00 normal hour
        ("MEMBER Peak hour", member_user, 8),     # 08:00 peak hour
        ("CASUAL Normal hour", casual_user, 14),
        ("CASUAL Peak hour", casual_user, 8),
    ]

    for label, user, hour in test_cases:
        trip = Trip(
            f"{label.replace(' ', '-')}-{user.id}",
            user,
            demo_bike,
            station,
            station,
            start_time=datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0),
            end_time=datetime.now().replace(hour=hour, minute=30, second=0, microsecond=0),
            distance_km=5
        )
        cost = system.calculate_trip_cost(trip)
        print(f"{label}: User {user.name} ({user.user_type}), Trip distance: {trip.distance_km} km, Cost: €{cost:.2f}")

if __name__ == "__main__":
    test_pricing_combinations()
