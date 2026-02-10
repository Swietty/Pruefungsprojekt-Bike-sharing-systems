from datetime import datetime, timedelta

from system import BikeShareSystem
from factories import BikeFactory, UserFactory
from models import Station, Trip, MaintenanceRecord, MaintenanceType
from pricing import CasualPricing
from analyzer import DataAnalyzer


def main():
    analyzer = DataAnalyzer()
    analyzer.load_data()
    analyzer.inspect()
    analyzer.clean_all()
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

    print(f"Trip cost: €{cost:.2f}")
    print(system)


if __name__ == "__main__":
    main()
