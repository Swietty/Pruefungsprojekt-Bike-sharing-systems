from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum

from utils import (
    validate_positive,
    validate_non_negative,
    validate_range,
    validate_non_empty_string,
    validate_email,
    validate_enum,
    validate_datetime_order
)

# ============================================================
# Enums
# ============================================================

class BikeStatus(Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"


class BikeType(Enum):
    CLASSIC = "classic"
    ELECTRIC = "electric"


class UserType(Enum):
    CASUAL = "casual"
    MEMBER = "member"


class MembershipTier(Enum):
    BASIC = "basic"
    PREMIUM = "premium"


class MaintenanceType(Enum):
    REPAIR = "repair"
    CLEANING = "cleaning"
    INSPECTION = "inspection"
    REPLACEMENT = "replacement"


# ============================================================
# Base Entity
# ============================================================

class Entity(ABC):
    _id_counter = {}

    def __init__(self, entity_id: Optional[str] = None):
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


# ============================================================
# Bike Hierarchy
# ============================================================

class Bike(Entity):

    def __init__(
        self,
        bike_id: Optional[str] = None,
        bike_type: BikeType = BikeType.CLASSIC,
        status: BikeStatus = BikeStatus.AVAILABLE
    ):
        super().__init__(bike_id)

        self._bike_type = validate_enum(bike_type, BikeType, "bike_type")
        self._status = validate_enum(status, BikeStatus, "status")

    @property
    def bike_id(self):
        return self.id

    @property
    def bike_type(self):
        return self._bike_type

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = validate_enum(value, BikeStatus, "status")

    def __str__(self):
        return f"Bike {self.bike_id} ({self.bike_type.value}) - {self.status.value}"

    def __repr__(self):
        return f"Bike(id={self.id!r}, type={self.bike_type.value!r}, status={self.status.value!r})"


class ClassicBike(Bike):

    def __init__(
        self,
        bike_id: Optional[str] = None,
        status: BikeStatus = BikeStatus.AVAILABLE,
        gear_count: int = 21
    ):
        super().__init__(bike_id, BikeType.CLASSIC, status)
        self._gear_count = validate_positive(gear_count, "gear_count")

    @property
    def gear_count(self):
        return self._gear_count

    def __str__(self):
        return f"ClassicBike {self.bike_id} ({self.gear_count}-gear) - {self.status.value}"

    def __repr__(self):
        return f"ClassicBike(id={self.id!r}, status={self.status.value!r}, gear_count={self.gear_count})"


class ElectricBike(Bike):

    def __init__(
        self,
        bike_id: Optional[str] = None,
        status: BikeStatus = BikeStatus.AVAILABLE,
        battery_level: float = 100.0,
        max_range_km: float = 50.0
    ):
        super().__init__(bike_id, BikeType.ELECTRIC, status)

        self._battery_level = validate_range(battery_level, 0, 100, "battery_level")
        self._max_range_km = validate_positive(max_range_km, "max_range_km")

    @property
    def battery_level(self):
        return self._battery_level

    @battery_level.setter
    def battery_level(self, value):
        self._battery_level = validate_range(value, 0, 100, "battery_level")

    @property
    def max_range_km(self):
        return self._max_range_km

    def __str__(self):
        return (
            f"EBike {self.bike_id} "
            f"({self.battery_level}% battery, {self.max_range_km}km) "
            f"- {self.status.value}"
        )

    def __repr__(self):
        return (
            f"ElectricBike(id={self.id!r}, status={self.status.value!r}, "
            f"battery_level={self.battery_level}, max_range_km={self.max_range_km})"
        )


# ============================================================
# Station
# ============================================================

class Station(Entity):

    def __init__(
        self,
        station_id: Optional[str] = None,
        name: str = "",
        capacity: int = 20,
        latitude: float = 0.0,
        longitude: float = 0.0
    ):
        super().__init__(station_id)

        self._name = validate_non_empty_string(name, "station_name")
        self._capacity = validate_positive(capacity, "capacity")
        self._latitude = latitude
        self._longitude = longitude
        self._available_bikes: List[Bike] = []

    @property
    def name(self):
        return self._name

    @property
    def capacity(self):
        return self._capacity

    @property
    def available_bikes(self):
        return self._available_bikes.copy()

    @property
    def available_count(self):
        return len(self._available_bikes)

    def add_bike(self, bike: Bike):
        if self.available_count >= self.capacity:
            raise ValueError("Station is full")
        self._available_bikes.append(bike)

    def remove_bike(self, bike: Bike):
        self._available_bikes.remove(bike)

    def __str__(self):
        return f"Station {self.name}: {self.available_count}/{self.capacity} bikes"

    def __repr__(self):
        return f"Station(id={self.id!r}, name={self.name!r}, capacity={self.capacity})"


# ============================================================
# User Hierarchy
# ============================================================

class User(Entity, ABC):

    def __init__(
        self,
        user_id: Optional[str] = None,
        name: str = "",
        email: str = "",
        user_type: UserType = UserType.CASUAL
    ):
        super().__init__(user_id)

        self._name = validate_non_empty_string(name, "user_name")
        self._email = validate_email(email)
        self._user_type = validate_enum(user_type, UserType, "user_type")
        self._trips: List["Trip"] = []

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def user_type(self):
        return self._user_type

    @property
    def trips(self):
        return self._trips.copy()

    def add_trip(self, trip: "Trip"):
        self._trips.append(trip)


class CasualUser(User):

    def __init__(
        self,
        user_id: Optional[str] = None,
        name: str = "",
        email: str = "",
        day_pass_count: int = 0
    ):
        super().__init__(user_id, name, email, UserType.CASUAL)
        self._day_pass_count = validate_non_negative(day_pass_count, "day_pass_count")

    @property
    def day_pass_count(self):
        return self._day_pass_count

    def __str__(self):
        return f"CasualUser {self.id} ({self.name})"

    def __repr__(self):
        return f"CasualUser(id={self.id!r}, name={self.name!r})"


class MemberUser(User):

    def __init__(
        self,
        user_id: Optional[str] = None,
        name: str = "",
        email: str = "",
        membership_start: Optional[datetime] = None,
        membership_end: Optional[datetime] = None,
        tier: MembershipTier = MembershipTier.BASIC
    ):
        super().__init__(user_id, name, email, UserType.MEMBER)

        self._membership_start = membership_start or datetime.now()
        self._membership_end = membership_end or (
            self._membership_start + timedelta(days=365)
        )

        validate_datetime_order(self._membership_start, self._membership_end)

        self._tier = validate_enum(tier, MembershipTier, "tier")

    @property
    def is_active(self):
        return self._membership_start <= datetime.now() <= self._membership_end

    def __str__(self):
        return f"MemberUser {self.id} ({self.name}) - {self._tier.value}"

    def __repr__(self):
        return f"MemberUser(id={self.id!r}, tier={self._tier.value!r})"


# ============================================================
# Trip
# ============================================================

class Trip(Entity):

    def __init__(
        self,
        trip_id: Optional[str],
        user: User,
        bike: Bike,
        start_station: Station,
        end_station: Station,
        start_time: datetime,
        end_time: datetime,
        distance_km: float = 0.0
    ):
        super().__init__(trip_id)

        validate_datetime_order(start_time, end_time)

        self.user = user
        self.bike = bike
        self.start_station = start_station
        self.end_station = end_station
        self.start_time = start_time
        self.end_time = end_time
        self.distance_km = validate_non_negative(distance_km, "distance_km")

    @property
    def duration_minutes(self):
        return int((self.end_time - self.start_time).total_seconds() / 60)

    def __str__(self):
        return f"Trip {self.id}: {self.user.name} - {self.duration_minutes} min"

    def __repr__(self):
        return f"Trip(id={self.id!r}, user={self.user.id!r})"


# ============================================================
# Maintenance Record
# ============================================================

class MaintenanceRecord(Entity):

    def __init__(
        self,
        record_id: Optional[str],
        bike: Bike,
        date: datetime,
        maintenance_type: MaintenanceType,
        cost: float = 0.0,
        description: str = ""
    ):
        super().__init__(record_id)

        self.bike = bike
        self.date = date
        self.maintenance_type = validate_enum(
            maintenance_type, MaintenanceType, "maintenance_type"
        )
        self.cost = validate_non_negative(cost, "cost")
        self.description = description

    def __str__(self):
        return f"Maintenance {self.id} - {self.maintenance_type.value}"

    def __repr__(self):
        return f"MaintenanceRecord(id={self.id!r}, type={self.maintenance_type.value!r})"
