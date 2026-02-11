from typing import Dict, Any
from models import Bike, ClassicBike, ElectricBike, BikeStatus, BikeType
from models import User, CasualUser, MemberUser, UserType, MembershipTier

# ============================================================================
# BikeFactory
# ============================================================================

class BikeFactory:
    """Factory for creating Bike objects from dictionaries."""

    @staticmethod  
    def create_from_dict(data: Dict[str, Any]) -> Bike:
        bike_id = data.get("bike_id")
        bike_type = data.get("bike_type", "classic")
        status_str = data.get("status", "available")

        status = BikeStatus[status_str.upper()] if isinstance(status_str, str) else status_str
        bike_type_enum = BikeType[bike_type.upper()] if isinstance(bike_type, str) else bike_type

        if bike_type_enum == BikeType.CLASSIC:
            return ClassicBike(bike_id=bike_id, status=status, gear_count=data.get("gear_count", 21))
        elif bike_type_enum == BikeType.ELECTRIC:
            return ElectricBike(
                bike_id=bike_id,
                status=status,
                battery_level=data.get("battery_level", 100.0),  
                max_range_km=data.get("max_range_km", 50.0) 
            )
        else:
            raise ValueError(f"Unknown bike_type: {bike_type_enum}")


# ============================================================================
# UserFactory
# ============================================================================

class UserFactory:
    """Factory for creating User objects from dictionaries."""
    @staticmethod
    def create_from_dict(data: Dict[str, Any]) -> User:
        
        # change user_type to enum if it's a string
        user_id = data.get("user_id")  
        name = data.get("name", "") 
        email = data.get("email", "")  
        user_type_str = data.get("user_type", "casual")  
        
        #  Convert string  to UserType enum if necessary
        user_type_enum = UserType[user_type_str.upper()] if isinstance(user_type_str, str) else user_type_str

        # Ensure email is present and looks valid; if not, provide a fallback
        if not isinstance(email, str) or "@" not in email:
            email = f"{user_id}@example.com"

        if user_type_enum == UserType.CASUAL:
            return CasualUser(user_id=user_id, name=name, email=email, day_pass_count=data.get("day_pass_count", 0))
        elif user_type_enum == UserType.MEMBER:
            tier_str = data.get("tier", "basic")
            tier = MembershipTier[tier_str.upper()] if isinstance(tier_str, str) else tier_str
            
            return MemberUser(
                user_id=user_id,
                name=name,
                email=email,
                membership_start=data.get("membership_start"),  
                membership_end=data.get("membership_end"),   
                tier=tier  
            )
        else:
            raise ValueError(f"Unknown user_type: {user_type_enum}")
