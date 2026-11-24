import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database.db import get_db_connection

# Designated Single Place: Vijay Nagar Square & Bombay Hospital Corridor, Indore (Madhya Pradesh)
DESIGNATED_STUDY_AREA = "Vijay Nagar Square & Bombay Hospital Corridor, Indore (M.P.)"

# Corridors centered around Vijay Nagar Square and connecting arterial junctions
INDORE_CORRIDORS = [
    {
        "location_name": "Vijay Nagar Square - AB Road BRTS",
        "landmark": "Near Vijay Nagar Metro Station & BRTS Cut",
        "base_lat": 22.7533,
        "base_lng": 75.8937,
        "causes": ["Signal Jump", "Over-speeding", "BRTS Dedicated Lane Intrusion"],
        "recommended_action": "Install automated red-light enforcement cameras and synchronize BRTS bus signal timing."
    },
    {
        "location_name": "Vijay Nagar Square - C21 Mall Side",
        "landmark": "Opposite Malhar Mega Mall entry cut",
        "base_lat": 22.7521,
        "base_lng": 75.8948,
        "causes": ["Distracted Driving", "Pedestrian Crossing", "Sudden Braking"],
        "recommended_action": "Erect pedestrian guard rails and pedestrian zebra crossing with timer signals."
    },
    {
        "location_name": "Scheme 54 - Bombay Hospital Junction",
        "landmark": "Near Bombay Hospital Service Road",
        "base_lat": 22.7590,
        "base_lng": 75.8980,
        "causes": ["Over-speeding", "Pothole / Road Defect", "Wet / Waterlogged"],
        "recommended_action": "Repair asphalt surface and install rumble strips prior to hospital ambulance entry."
    },
    {
        "location_name": "Radisson Square - Ring Road Link",
        "landmark": "Radisson Blu Rotary heading to Vijay Nagar",
        "base_lat": 22.7441,
        "base_lng": 75.8988,
        "causes": ["Over-speeding", "Heavy Truck Turnover", "Night / Low Light"],
        "recommended_action": "Install high-mast LED lighting and chevron reflective arrow boards on rotary curve."
    },
    {
        "location_name": "MR-10 Junction (Vijay Nagar Bypass)",
        "landmark": "Chandra Gupta Maurya Square approach",
        "base_lat": 22.7635,
        "base_lng": 75.8890,
        "causes": ["Over-speeding", "Heavy Truck Collision", "Brake Failure"],
        "recommended_action": "Deploy radar speed display boards and height barriers for heavy freight vehicles."
    },
    {
        "location_name": "Rasoma Square - Vijay Nagar Link",
        "landmark": "Near Medanta Hospital corridor",
        "base_lat": 22.7585,
        "base_lng": 75.8970,
        "causes": ["Signal Jump", "Two-Wheeler Skidding", "Distracted Driving"],
        "recommended_action": "Recalibrate traffic signal cycle and repaint thermo-plastic lane guidance markings."
    },
    {
        "location_name": "Meghdoot Garden Crossing",
        "landmark": "Vijay Nagar to Scheme 54 feeder road",
        "base_lat": 22.7510,
        "base_lng": 75.8885,
        "causes": ["Pedestrian Crossing", "Over-speeding in recreational zone", "Poor Visibility"],
        "recommended_action": "20 km/h speed calming humps and pedestrian warning blinkers."
    }
]

VEHICLE_TYPES = [
    "Two-Wheeler",
    "Four-Wheeler / Car",
    "Auto-Rickshaw",
    "Commercial Bus (iBus / City Bus)",
    "Heavy Truck",
    "Multiple Vehicles"
]

ROAD_CONDITIONS = [
    "Dry & Normal",
    "Wet / Waterlogged",
    "Potholed & Damaged",
    "BRTS Corridor Interface",
    "Poor Street Lighting"
]

WEATHER_CONDITIONS = [
    "Clear / Sunny",
    "Rainy / Monsoon",
    "Heavy Fog / Mist",
    "Night / Dark"
]

FEED_SOURCES = [
    "Indore Smart City ICCC Automated Feed #07",
    "Indore Traffic Police - Vijay Nagar Square CCTV AI",
    "Emergency 112 / Dial 100 Indore Dispatch",
    "BRTS Corridor Sensor (Vijay Nagar Hub)",
    "Vijay Nagar Traffic Booth Automated Sensor"
]

SEVERITY_POOL = ["Minor", "Minor", "Major", "Major", "Fatal"]

def generate_random_accident() -> Dict[str, Any]:
    """Generates a realistic accident record situated strictly at Vijay Nagar Square & Bombay Hospital Corridor, Indore."""
    corridor = random.choice(INDORE_CORRIDORS)
    
    # Small realistic coordinate jitter along the junction (approx 30-150 meters)
    lat_jitter = random.uniform(-0.0018, 0.0018)
    lng_jitter = random.uniform(-0.0018, 0.0018)
    
    latitude = round(corridor["base_lat"] + lat_jitter, 5)
    longitude = round(corridor["base_lng"] + lng_jitter, 5)
    
    severity = random.choice(SEVERITY_POOL)
    vehicle = random.choice(VEHICLE_TYPES)
    cause = random.choice(corridor["causes"])
    road_cond = random.choice(ROAD_CONDITIONS)
    weather_cond = random.choice(WEATHER_CONDITIONS)
    
    if severity == "Fatal":
        casualties = 1
        injuries = random.randint(1, 2)
    elif severity == "Major":
        casualties = 0
        injuries = random.randint(1, 3)
    else:
        casualties = 0
        injuries = random.randint(0, 1)

    now = datetime.now()
    random_minutes = random.randint(0, 90)
    incident_time = now - timedelta(minutes=random_minutes)
    date_str = incident_time.strftime("%Y-%m-%d")
    time_str = incident_time.strftime("%H:%M")

    source = random.choice(FEED_SOURCES)
    title = f"{vehicle} crash at {corridor['location_name']}"

    description = (
        f"Automated smart city detection: {vehicle} involved in an incident near {corridor['landmark']}. "
        f"Suspected cause: {cause}. Road status: '{road_cond}' during '{weather_cond}' weather. "
        f"Detected automatically by {source}."
    )

    return {
        "title": title,
        "location_name": corridor["location_name"],
        "landmark": corridor["landmark"],
        "latitude": latitude,
        "longitude": longitude,
        "accident_date": date_str,
        "accident_time": time_str,
        "severity": severity,
        "vehicle_type": vehicle,
        "road_condition": road_cond,
        "weather_condition": weather_cond,
        "casualties_count": casualties,
        "injuries_count": injuries,
        "description": description,
        "possible_cause": cause,
        "reported_by_id": 1,
        "reporter_name": source,
        "reporter_contact": "Indore Police Control (+91 731 2522222)",
        "status": "Verified" if severity in ["Major", "Fatal"] else "Pending",
        "admin_notes": f"Automatically ingested via {source}. Location verified at Vijay Nagar - Bombay Hospital Corridor, Indore."
    }

def auto_feed_accidents(count: int = 1) -> List[Dict[str, Any]]:
    """Inserts `count` simulated automated accidents for Vijay Nagar & Bombay Hospital Corridor, Indore into SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    inserted_records = []
    
    for _ in range(count):
        acc = generate_random_accident()
        cursor.execute(
            """
            INSERT INTO accidents (
                title, location_name, landmark, latitude, longitude,
                accident_date, accident_time, severity, vehicle_type,
                road_condition, weather_condition, casualties_count,
                injuries_count, description, possible_cause, reported_by_id,
                reporter_name, reporter_contact, status, admin_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                acc["title"],
                acc["location_name"],
                acc["landmark"],
                acc["latitude"],
                acc["longitude"],
                acc["accident_date"],
                acc["accident_time"],
                acc["severity"],
                acc["vehicle_type"],
                acc["road_condition"],
                acc["weather_condition"],
                acc["casualties_count"],
                acc["injuries_count"],
                acc["description"],
                acc["possible_cause"],
                acc["reported_by_id"],
                acc["reporter_name"],
                acc["reporter_contact"],
                acc["status"],
                acc["admin_notes"]
            )
        )
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM accidents WHERE id = ?", (new_id,))
        inserted_records.append(dict(cursor.fetchone()))

    conn.commit()
    conn.close()
    
    return inserted_records
