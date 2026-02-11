from typing import Dict, List, TYPE_CHECKING
from datetime import datetime
from models import Bike, Station, User, Trip, MaintenanceRecord, BikeStatus
from pricing import PricingStrategy, CasualPricing
from factories import BikeFactory, UserFactory

if TYPE_CHECKING:
    from analyzer import DataAnalyzer


class BikeShareSystem:
    """main class representing the bike sharing system. It manages bikes, stations, users, trips, and maintenance records."""

    def __init__(self):
        """Initialize an empty bike sharing system."""
        self.bikes: Dict[str, Bike] = {}
        
        # Station storage
        self.stations: Dict[str, Station] = {}
        
        # User storage: {"user_id": User}
        self.users: Dict[str, User] = {}
        
        # Trip history: List[Trip] 
        self.trips: List[Trip] = []
        
        # Maintenance history: List[MaintenanceRecord]
        self.maintenance_records: List[MaintenanceRecord] = []
        
        # Pricing strategy: CasualPricing, MemberPricing , PeakHourPricing
        self.pricing_strategy: PricingStrategy = CasualPricing()

    # ============================================================
    # ADD METHODS
    # ============================================================

    def add_bike(self, bike: Bike):
        self.bikes[bike.id] = bike  

    def add_station(self, station: Station):
        self.stations[station.id] = station  

    def add_user(self, user: User):
        """Add a user to the system.
        
        Args:
            user: User object (CasualUser or MemberUser)
        
        Note:
            User is stored in a dictionary with ID as the key.
        """
        self.users[user.id] = user  

    # ============================================================
    # RECORD METHODS
    # ============================================================

    def record_trip(self, trip: Trip):
        """Record a new trip in the system.
        
        Called when a user completes a trip.
        This is important for:
        - Statistics (which routes are popular)
        - Cost calculation
        - User history
        
        Args:
            trip: Trip object with information about time, distance and participants
        
        Side effects:
        - Adds trip to trips history
        - Adds trip to user history (trip.user.add_trip)
        """
        # Add trip to global list
        self.trips.append(trip)
        # Add trip to specific user history
        # User should know all their trips
        trip.user.add_trip(trip)

    def record_maintenance(self, record: MaintenanceRecord):
        """Record bike maintenance.
        
        Called when a bicycle goes for repair or cleaning.
        
        Args:
            record: Maintenance record with information about work type and cost
        
        Side effects:
        - Adds record to maintenance_records history
        - Changes bike status to MAINTENANCE
        """
        # Add maintenance record to history
        self.maintenance_records.append(record)
        # Mark that bike is currently under maintenance
        # System knows it cannot be taken
        record.bike.status = BikeStatus.MAINTENANCE  

    # ============================================================ 
    # STRATEGY MANAGEMENT METHODS
    # ============================================================

    def set_pricing_strategy(self, strategy: PricingStrategy):
        """Change pricing strategy.
        
        Allows dynamically changing how trip costs are calculated.
        
        Args:
            strategy: Strategy object (CasualPricing, MemberPricing or PeakHourPricing)
        
        Examples:
            # Use regular prices for casual users
            system.set_pricing_strategy(CasualPricing())
            
            # Use discounted prices for members
            system.set_pricing_strategy(MemberPricing())
            
            # 8am to 9am - peak hour surcharge
            system.set_pricing_strategy(PeakHourPricing())
        """
        self.pricing_strategy = strategy

    def calculate_trip_cost(self, trip: Trip) -> float:
        """Calculate trip cost.
        
        Uses current pricing strategy for calculation.
        
        Args:
            trip: Trip object with information about time and distance
        
        Returns:
            float: Trip cost in euros
        
        Note:
            Cost depends on strategy! For one trip,
            different strategies will give different prices.
        """
        # Delegate calculation to current strategy
        # Strategy knows how to calculate cost
        return self.pricing_strategy.calculate_cost(trip)

    # ============================================================
    # INTEGRATION METHODS
    # ============================================================

    def load_from_analyzer(self, analyzer: "DataAnalyzer") -> None:
        """Load data from DataAnalyzer into the system.
        
        This is an integration method that:
        - Takes pandas DataFrame from analyzer
        - Converts it to model objects (User, Station)
        - Uses factories for creation
        - Adds everything to the system
        
        Example usage in main.py:
            analyzer = DataAnalyzer()
            analyzer.load_data()
            analyzer._clean_trips()
            
            system = BikeShareSystem()
            system.load_from_analyzer(analyzer)  # ← This loads everything!
        
        Args:
            analyzer: DataAnalyzer object with loaded CSV data
        
        Note:
            This solves the problem: "How to transform from pandas DataFrame (from CSV)
            to our model objects (User, Station)?"
            Answer: load_from_analyzer() which uses factories!
        """
        # LOAD USERS FROM CSV
        if analyzer.trips is not None:  # If there is trip data
            # Group by user_id and get first trip of each user
            # This is needed because each row is a trip, not a user
            users_data = analyzer.trips.groupby("user_id").first().reset_index()
            
            for _, row in users_data.iterrows():
                try:
                    user_dict = row.to_dict()
                    # Ensure name is set properly
                    if not user_dict.get("name"):
                        user_dict["name"] = user_dict.get("user_name") or ("Anonymous_" + str(user_dict.get("user_id")))

                    # use factory to create user object from dict
                    user = UserFactory.create_from_dict(user_dict)
                    # add user to system
                    self.add_user(user)
                except Exception as e:
                    # if error - skip this user and continue
                    print(f"  Failed to create user {row.get('user_id')}: {e}")
        
        # load stations from CSV
        if analyzer.stations is not None: 
            for _, row in analyzer.stations.iterrows():
                try:
                    station = Station(
                        station_id=row.get("station_id"),
                        name=row.get("station_name", "Unknown"),
                        capacity=int(row.get("capacity", 20))
                    )
                    # add station to system
                    self.add_station(station)
                except Exception as e:
                    # if error - skip this station and continue
                    print(f" Failed to create station {row.get('station_id')}: {e}")

    # ============================================================
    # STRING METHODS
    # ============================================================

    def __str__(self):
        return (f"BikeShareSystem: {len(self.bikes)} bikes, {len(self.stations)} stations, "
                f"{len(self.users)} users, {len(self.trips)} trips, "
                f"Strategy: {self.pricing_strategy.get_name()}")

    def __repr__(self):
        return (f"BikeShareSystem(bikes={len(self.bikes)}, stations={len(self.stations)}, "
                f"users={len(self.users)}, trips={len(self.trips)}, "
                f"maintenance_records={len(self.maintenance_records)}, "
                f"pricing_strategy={self.pricing_strategy!r})")
