import re
from typing import Dict, Any, Tuple, List

VALID_SEVERITIES = {"Minor", "Major", "Fatal"}
VALID_STATUSES = {"Pending", "Verified", "Under Investigation", "Resolved", "Rejected"}

def validate_accident_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates submitted accident report fields for completeness, valid ranges, and types.
    Returns (is_valid, list_of_errors).
    """
    errors = []

    # 1. Title & Location validation
    title = str(data.get("title", "")).strip()
    if not title:
        errors.append("Incident title is required.")
    elif len(title) < 5:
        errors.append("Title should be at least 5 characters long.")

    location_name = str(data.get("location_name", "")).strip()
    if not location_name:
        errors.append("Location name or address is required.")

    # 2. Coordinates validation
    try:
        lat = float(data.get("latitude", 0))
        lng = float(data.get("longitude", 0))
        if not (-90.0 <= lat <= 90.0):
            errors.append("Latitude must be between -90 and 90 degrees.")
        if not (-180.0 <= lng <= 180.0):
            errors.append("Longitude must be between -180 and 180 degrees.")
        if lat == 0.0 and lng == 0.0:
            errors.append("Please specify a valid GPS coordinate on the map.")
    except (ValueError, TypeError):
        errors.append("Coordinates (latitude and longitude) must be valid decimal numbers.")

    # 3. Date & Time validation
    date = str(data.get("accident_date", "")).strip()
    if not date:
        errors.append("Accident date is required.")
    elif not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        errors.append("Accident date must follow YYYY-MM-DD format.")

    time = str(data.get("accident_time", "")).strip()
    if not time:
        errors.append("Accident time is required.")

    # 4. Severity validation
    severity = str(data.get("severity", "")).strip()
    if not severity:
        errors.append("Accident severity is required.")
    elif severity not in VALID_SEVERITIES:
        errors.append(f"Severity must be one of: {', '.join(VALID_SEVERITIES)}.")

    # 5. Casualties & Injuries validation
    try:
        casualties = int(data.get("casualties_count", 0))
        if casualties < 0:
            errors.append("Casualties count cannot be negative.")
    except (ValueError, TypeError):
        errors.append("Casualties count must be an integer.")

    try:
        injuries = int(data.get("injuries_count", 0))
        if injuries < 0:
            errors.append("Injuries count cannot be negative.")
    except (ValueError, TypeError):
        errors.append("Injuries count must be an integer.")

    return len(errors) == 0, errors

def validate_user_registration(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates user registration input.
    """
    errors = []
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))
    full_name = str(data.get("full_name", "")).strip()

    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    if not email or "@" not in email or "." not in email:
        errors.append("A valid email address is required.")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if not full_name:
        errors.append("Full name is required.")

    return len(errors) == 0, errors
