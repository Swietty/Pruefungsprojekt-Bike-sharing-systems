from typing import Dict, List, TYPE_CHECKING
from datetime import datetime

from models import Bike, Station, User, Trip, MaintenanceRecord, BikeStatus, UserType
from pricing import CasualPricing, MemberPricing, PeakHourPricing
from factories import UserFactory

if TYPE_CHECKING:
    from analyzer import DataAnalyzer


class BikeShareSystem:
    """
    Main class representing the bike sharing system.
    Manages bikes, stations, users, trips, and maintenance records.
    """

    def __init__(self):
        """Initialize an empty bike sharing system."""

        self.bikes: Dict[str, Bike] = {}
        self.stations: Dict[str, Station] = {}
        self.users: Dict[str, User] = {}
        self.trips: List[Trip] = []
        self.maintenance_records: List[MaintenanceRecord] = []

        # Pre-create pricing strategies (clean and efficient)
        self._casual_pricing = CasualPricing()
        self._member_pricing = MemberPricing()
        self._peak_pricing = PeakHourPricing()

    # ============================================================
    # ADD METHODS
    # ============================================================

    def add_bike(self, bike: Bike):
        self.bikes[bike.id] = bike

    def add_station(self, station: Station):
        self.stations[station.id] = station

    def add_user(self, user: User):
        self.users[user.id] = user

    # ============================================================
    # RECORD METHODS
    # ============================================================

    def record_trip(self, trip: Trip):
        """Record completed trip."""
        self.trips.append(trip)
        trip.user.add_trip(trip)

    def record_maintenance(self, record: MaintenanceRecord):
        """Record bike maintenance."""
        self.maintenance_records.append(record)
        record.bike.status = BikeStatus.MAINTENANCE

    # ============================================================
    # PRICING LOGIC
    # ============================================================

    def is_peak_hour(self, dt: datetime) -> bool:
        """Check if given time is peak hour."""
        return dt.hour in range(7, 11) or dt.hour in range(17, 21)


    def calculate_trip_cost(self, trip: Trip) -> float:
        """
        Pricing logic:
        - Select base strategy (Member or Casual)
        - If peak hour → apply peak multiplier
        """

        # 1️⃣ Select base pricing strategy
        if trip.user.user_type == UserType.MEMBER:
            base_strategy = self._member_pricing
        else:
            base_strategy = self._casual_pricing

        # 2️⃣ Calculate base cost
        cost = base_strategy.calculate_cost(trip)

        # 3️⃣ Apply peak multiplier if needed
        if self.is_peak_hour(trip.start_time):
            peak_multiplier = 1.5
            cost *= peak_multiplier

        return cost

    # ============================================================
    # INTEGRATION WITH ANALYZER
    # ============================================================

    def load_from_analyzer(self, analyzer: "DataAnalyzer") -> None:
        """Load users and stations from DataAnalyzer."""

        # Load users
        if analyzer.trips is not None:
            users_data = analyzer.trips.groupby("user_id").first().reset_index()

            for _, row in users_data.iterrows():
                try:
                    user_dict = row.to_dict()

                    if not user_dict.get("name"):
                        user_dict["name"] = (
                            user_dict.get("user_name")
                            or f"Anonymous_{user_dict.get('user_id')}"
                        )

                    user = UserFactory.create_from_dict(user_dict)
                    self.add_user(user)

                except Exception as e:
                    print(f"Failed to create user {row.get('user_id')}: {e}")

        # Load stations
        if analyzer.stations is not None:
            for _, row in analyzer.stations.iterrows():
                try:
                    station = Station(
                        station_id=row.get("station_id"),
                        name=row.get("station_name", "Unknown"),
                        capacity=int(row.get("capacity", 20)),
                    )
                    self.add_station(station)

                except Exception as e:
                    print(f"Failed to create station {row.get('station_id')}: {e}")

    # ============================================================
    # STRING METHODS
    # ============================================================

    def __str__(self):
        return (
            f"BikeShareSystem: {len(self.bikes)} bikes, "
            f"{len(self.stations)} stations, "
            f"{len(self.users)} users, "
            f"{len(self.trips)} trips"
        )

    def __repr__(self):
        return (
            f"BikeShareSystem("
            f"bikes={len(self.bikes)}, "
            f"stations={len(self.stations)}, "
            f"users={len(self.users)}, "
            f"trips={len(self.trips)}, "
            f"maintenance_records={len(self.maintenance_records)})"
        )
