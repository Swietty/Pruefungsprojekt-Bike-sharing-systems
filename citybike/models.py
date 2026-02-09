from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import re

# Enums

class BikeStatus(Enum):
    """Enumeration for bike status."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"


class BikeType(Enum):
    """Enumeration for bike types."""
    CLASSIC = "classic"
    ELECTRIC = "electric"


class UserType(Enum):
    """Enumeration for user types."""
    CASUAL = "casual"
    MEMBER = "member"


class MembershipTier(Enum):
    """Enumeration for membership tiers."""
    BASIC = "basic"
    PREMIUM = "premium"


class MaintenanceType(Enum):
    """Enumeration for maintenance types."""
    REPAIR = "repair"
    CLEANING = "cleaning"
    INSPECTION = "inspection"
    REPLACEMENT = "replacement"


# Abstract Base Class: Entity

class Entity(ABC):
    _id_counter = {}

    def __init__(self, entity_id: Optional[str] = None):
        if entity_id is not None and not str(entity_id).strip():
            raise ValueError("Entity ID cannot be empty string")
        self.id = entity_id or self._generate_id()
        self.created_at = datetime.now()

    def _generate_id(self) -> str:
        cls_name = self.__class__.__name__
        Entity._id_counter[cls_name] = Entity._id_counter.get(cls_name, 0) + 1
        return f"{cls_name.lower()}_{Entity._id_counter[cls_name]}"

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


# Bike Hierarchy

class Bike(Entity):
    def __init__(self, bike_id: Optional[str] = None,
                 bike_type: BikeType = BikeType.CLASSIC,
                 status: BikeStatus = BikeStatus.AVAILABLE):
        super().__init__(bike_id)
        if not isinstance(bike_type, BikeType):
            raise ValueError("Invalid bike_type")
        if not isinstance(status, BikeStatus):
            raise ValueError("Invalid status")
        self._bike_type = bike_type
        self._status = status

    @property
    def bike_id(self): return self.id
    @property
    def bike_type(self): return self._bike_type
    @property
    def status(self): return self._status
    @status.setter
    def status(self, value): 
        if not isinstance(value, BikeStatus):
            raise ValueError("Invalid status")
        self._status = value

    def __str__(self): return f"Bike {self.bike_id} ({self.bike_type.value}) - {self.status.value}"
    def __repr__(self): return f"Bike(id={self.id!r}, type={self.bike_type.value!r}, status={self.status.value!r})"


class ClassicBike(Bike):
    def __init__(self, bike_id: Optional[str] = None,
                 status: BikeStatus = BikeStatus.AVAILABLE,
                 gear_count: int = 21):
        super().__init__(bike_id, BikeType.CLASSIC, status)
        if gear_count <= 0:
            raise ValueError("gear_count must be positive")
        self._gear_count = gear_count

    @property
    def gear_count(self): return self._gear_count

    def __str__(self): return f"ClassicBike {self.bike_id} ({self.gear_count}-gear) - {self.status.value}"
    def __repr__(self): return f"ClassicBike(id={self.id!r}, status={self.status.value!r}, gear_count={self.gear_count})"


class ElectricBike(Bike):
    def __init__(self, bike_id: Optional[str] = None,
                 status: BikeStatus = BikeStatus.AVAILABLE,
                 battery_level: float = 100.0,
                 max_range_km: float = 50.0):
        super().__init__(bike_id, BikeType.ELECTRIC, status)
        if not (0 <= battery_level <= 100): raise ValueError("battery_level must be 0-100")
        if max_range_km <= 0: raise ValueError("max_range_km must be positive")
        self._battery_level = battery_level
        self._max_range_km = max_range_km

    @property
    def battery_level(self): return self._battery_level
    @battery_level.setter
    def battery_level(self, value):
        if not (0 <= value <= 100): raise ValueError("battery_level must be 0-100")
        self._battery_level = value

    @property
    def max_range_km(self): return self._max_range_km

    def __str__(self):
        return f"EBike {self.bike_id} ({self.battery_level}% battery, {self.max_range_km}km) - {self.status.value}"

    def __repr__(self):
        return (f"ElectricBike(id={self.id!r}, status={self.status.value!r}, "
                f"battery_level={self.battery_level}, max_range_km={self.max_range_km})")



# Station

class Station(Entity):
    def __init__(self, station_id: Optional[str] = None,
                 name: str = "", capacity: int = 20,
                 latitude: float = 0.0, longitude: float = 0.0):
        super().__init__(station_id)
        if not name.strip(): raise ValueError("Station name cannot be empty")
        if capacity <= 0: raise ValueError("Capacity must be positive")
        self._name = name.strip()
        self._capacity = capacity
        self._latitude = latitude
        self._longitude = longitude
        self._available_bikes: List[Bike] = []

    @property
    def station_id(self): return self.id
    @property
    def name(self): return self._name
    @property
    def capacity(self): return self._capacity
    @property
    def latitude(self): return self._latitude
    @property
    def longitude(self): return self._longitude
    @property
    def available_bikes(self): return self._available_bikes.copy()
    @property
    def available_count(self): return len(self._available_bikes)

    def add_bike(self, bike: Bike):
        if self.available_count >= self.capacity: raise ValueError("Station full")
        self._available_bikes.append(bike)

    def remove_bike(self, bike: Bike):
        self._available_bikes.remove(bike)

    def __str__(self):
        return f"Station {self.name} ({self.station_id}): {self.available_count}/{self.capacity} bikes"

    def __repr__(self):
        return f"Station(id={self.id!r}, name={self.name!r}, capacity={self.capacity}, available={self.available_count})"



# User Hierarchy

class User(Entity, ABC):
    EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    def __init__(self, user_id: Optional[str] = None, name: str = "", email: str = "", user_type: UserType = UserType.CASUAL):
        super().__init__(user_id)
        if not name.strip(): raise ValueError("User name cannot be empty")
        if not re.match(self.EMAIL_REGEX, email.strip()): raise ValueError("Invalid email")
        self._name = name.strip()
        self._email = email.strip()
        self._user_type = user_type
        self._trips: List['Trip'] = []

    @property
    def user_id(self): return self.id
    @property
    def name(self): return self._name
    @property
    def email(self): return self._email
    @property
    def user_type(self): return self._user_type
    @property
    def trips(self): return self._trips.copy()
    def add_trip(self, trip: 'Trip'): self._trips.append(trip)

    @abstractmethod
    def __str__(self): pass
    @abstractmethod
    def __repr__(self): pass


class CasualUser(User):
    def __init__(self, user_id: Optional[str] = None, name: str = "", email: str = "", day_pass_count: int = 0):
        super().__init__(user_id, name, email, UserType.CASUAL)
        if day_pass_count < 0: raise ValueError("day_pass_count must be non-negative")
        self._day_pass_count = day_pass_count

    @property
    def day_pass_count(self): return self._day_pass_count
    @day_pass_count.setter
    def day_pass_count(self, value): self._day_pass_count = value

    def __str__(self): return f"CasualUser {self.user_id} ({self.name}) - Day Passes: {self.day_pass_count}"
    def __repr__(self): return f"CasualUser(id={self.id!r}, name={self.name!r}, email={self.email!r}, day_pass_count={self.day_pass_count})"


class MemberUser(User):
    def __init__(self, user_id: Optional[str] = None, name: str = "", email: str = "",
                 membership_start: Optional[datetime] = None, membership_end: Optional[datetime] = None,
                 tier: MembershipTier = MembershipTier.BASIC):
        super().__init__(user_id, name, email, UserType.MEMBER)
        self._membership_start = membership_start or datetime.now()
        self._membership_end = membership_end or (self._membership_start + timedelta(days=365))
        if self._membership_end <= self._membership_start: raise ValueError("End must be after start")
        self._tier = tier

    @property
    def membership_start(self): return self._membership_start
    @property
    def membership_end(self): return self._membership_end
    @property
    def tier(self): return self._tier
    @tier.setter
    def tier(self, value): self._tier = value
    @property
    def is_active(self): return self.membership_start <= datetime.now() <= self.membership_end
    @property
    def days_remaining(self): return max(0, (self.membership_end - datetime.now()).days)

    def __str__(self): return f"MemberUser {self.user_id} ({self.name}) - Tier: {self.tier.value}, Status: {'Active' if self.is_active else 'Inactive'}"
    def __repr__(self): return f"MemberUser(id={self.id!r}, name={self.name!r}, email={self.email!r}, tier={self.tier.value!r})"




# Trip

class Trip:
    def __init__(self, trip_id: str, user: User, bike: Bike,
                 start_station: Station, end_station: Station,
                 start_time: datetime, end_time: datetime,
                 distance_km: float = 0.0):
        if end_time <= start_time: raise ValueError("end_time must be after start_time")
        self.trip_id = trip_id
        self.user = user
        self.bike = bike
        self.start_station = start_station
        self.end_station = end_station
        self.start_time = start_time
        self.end_time = end_time
        self.distance_km = distance_km

    @property
    def duration_minutes(self): return int((self.end_time - self.start_time).total_seconds() / 60)
    @property
    def duration_hours(self): return self.duration_minutes / 60

    def __str__(self): return f"Trip {self.trip_id}: {self.user.name} ({self.start_station.name} → {self.end_station.name}) {self.duration_minutes}min, {self.distance_km}km"
    def __repr__(self): return f"Trip(id={self.trip_id!r}, user={self.user.user_id!r}, bike={self.bike.bike_id!r})"




# Maintenance Record

class MaintenanceRecord:
    def __init__(self, record_id: str, bike: Bike, date: datetime,
                 maintenance_type: MaintenanceType, cost: float = 0.0,
                 description: str = ""):
        self.record_id = record_id
        self.bike = bike
        self.date = date
        self.maintenance_type = maintenance_type
        self.cost = cost
        self.description = description

    def __str__(self): return f"MaintenanceRecord {self.record_id}: Bike {self.bike.bike_id} - {self.maintenance_type.value} on {self.date.date()} (${self.cost})"
    def __repr__(self): return f"MaintenanceRecord(id={self.record_id!r}, bike={self.bike.bike_id!r}, type={self.maintenance_type.value!r})"

