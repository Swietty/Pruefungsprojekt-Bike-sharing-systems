from typing import Dict, List
from models import Bike, Station, User, Trip, MaintenanceRecord, BikeStatus
from pricing import PricingStrategy, CasualPricing

class BikeShareSystem:
    """Main orchestration class for the bike sharing system."""

    def __init__(self):
        self.bikes: Dict[str, Bike] = {}
        self.stations: Dict[str, Station] = {}
        self.users: Dict[str, User] = {}
        self.trips: List[Trip] = []
        self.maintenance_records: List[MaintenanceRecord] = []
        self.pricing_strategy: PricingStrategy = CasualPricing()

    def add_bike(self, bike: Bike):
        self.bikes[bike.id] = bike  

    def add_station(self, station: Station):
        self.stations[station.id] = station  

    def add_user(self, user: User):
        self.users[user.id] = user  

    def record_trip(self, trip: Trip):
        self.trips.append(trip)
        trip.user.add_trip(trip)

    def record_maintenance(self, record: MaintenanceRecord):
        self.maintenance_records.append(record)
        record.bike.status = BikeStatus.MAINTENANCE  

    def set_pricing_strategy(self, strategy: PricingStrategy):
        self.pricing_strategy = strategy

    def calculate_trip_cost(self, trip: Trip) -> float:
        return self.pricing_strategy.calculate_cost(trip)

    def __str__(self):
        return (f"BikeShareSystem: {len(self.bikes)} bikes, {len(self.stations)} stations, "
                f"{len(self.users)} users, {len(self.trips)} trips, "
                f"Strategy: {self.pricing_strategy.get_name()}")

    def __repr__(self):
        return (f"BikeShareSystem(bikes={len(self.bikes)}, stations={len(self.stations)}, "
                f"users={len(self.users)}, trips={len(self.trips)}, "
                f"maintenance_records={len(self.maintenance_records)}, "
                f"pricing_strategy={self.pricing_strategy!r})")
