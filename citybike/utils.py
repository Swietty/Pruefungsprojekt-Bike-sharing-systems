import re
from datetime import datetime
from typing import Any
from enum import Enum


# ---------------------------------------------------------------------------
# Generic validators
# ---------------------------------------------------------------------------

def validate_positive(value: float, name: str = "value") -> float:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def validate_non_negative(value: float, name: str = "value") -> float:
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")
    return value


def validate_range(value: float, min_val: float, max_val: float, name: str = "value") -> float:
    if not (min_val <= value <= max_val):
        raise ValueError(f"{name} must be between {min_val} and {max_val}, got {value}")
    return value


def validate_non_empty_string(value: str, name: str = "value") -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def validate_email(email: str) -> str:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email: {email}")
    return email.strip()


def validate_enum(value: Any, enum_type: type[Enum], name: str = "value") -> Any:
    if not isinstance(value, enum_type):
        raise ValueError(f"{name} must be of type {enum_type.__name__}")
    return value


def validate_datetime_order(start: datetime, end: datetime) -> None:
    if end <= start:
        raise ValueError("end_time must be after start_time")
