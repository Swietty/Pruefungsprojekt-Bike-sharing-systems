from abc import ABC, abstractmethod
from models import Trip

# ============================================================================
# Abstract Base Class: PricingStrategy
# ============================================================================

class PricingStrategy(ABC):
    """Abstract base class for pricing strategies."""

    @abstractmethod
    def calculate_cost(self, trip: Trip) -> float:
        """Calculate cost of a trip."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the strategy."""
        pass


# ============================================================================
# Concrete Pricing Strategies
# ============================================================================

class CasualPricing(PricingStrategy):
    """Pricing strategy for casual users (pay-per-use)."""
    BASE_RATE_PER_MINUTE = 0.15
    MIN_CHARGE = 2.0

    def calculate_cost(self, trip: Trip) -> float:
        cost = trip.duration_minutes * self.BASE_RATE_PER_MINUTE
        return max(cost, self.MIN_CHARGE)

    def get_name(self) -> str:
        return "CasualPricing"

    def __repr__(self):
        return f"CasualPricing(${self.BASE_RATE_PER_MINUTE}/min, min=${self.MIN_CHARGE})"


class MemberPricing(PricingStrategy):
    """Pricing strategy for member users."""
    BASE_RATE_PER_MINUTE = 0.10
    DISTANCE_BONUS = 0.05

    def calculate_cost(self, trip: Trip) -> float:
        return trip.duration_minutes * self.BASE_RATE_PER_MINUTE + trip.distance_km * self.DISTANCE_BONUS

    def get_name(self) -> str:
        return "MemberPricing"

    def __repr__(self):
        return f"MemberPricing(${self.BASE_RATE_PER_MINUTE}/min, ${self.DISTANCE_BONUS}/km)"


class PeakHourPricing(PricingStrategy):
    """Pricing with surge pricing during peak hours."""
    BASE_RATE_PER_MINUTE = 0.25
    PEAK_MULTIPLIER = 1.5
    PEAK_HOURS = (8, 9, 17, 18)

    def calculate_cost(self, trip: Trip) -> float:
        cost = trip.duration_minutes * self.BASE_RATE_PER_MINUTE
        start_hour = trip.start_time.hour
        end_hour = trip.end_time.hour
        multiplier = self.PEAK_MULTIPLIER if start_hour in self.PEAK_HOURS or end_hour in self.PEAK_HOURS else 1.0
        return cost * multiplier

    def get_name(self) -> str:
        return "PeakHourPricing"

    def __repr__(self):
        return f"PeakHourPricing(${self.BASE_RATE_PER_MINUTE}/min, {self.PEAK_MULTIPLIER}x peak)"