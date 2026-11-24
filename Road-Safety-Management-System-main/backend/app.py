import os
import sys
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db import get_db_connection, init_db, hash_password
from utils.validation import validate_accident_data, validate_user_registration
from utils.hotspot_engine import compute_hotspots
from utils.auto_feeder import auto_feed_accidents, DESIGNATED_STUDY_AREA
from utils.open_api_generator import (
    generate_accidents_from_open_api,
    fetch_open_meteo_weather,
    fetch_osm_geographic_nodes
)

# Path to built frontend (if present)
FRONTEND_DIST = os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist")

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
CORS(app)

# Ensure DB is initialized
init_db()

# ============================================================================
# AUTHENTICATION ENDPOINTS (Step 1: User Registration & Login)
# ============================================================================

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    is_valid, errors = validate_user_registration(data)
    if not is_valid:
        return jsonify({"success": False, "errors": errors}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check existing user
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (data["username"], data["email"]))
    if cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "errors": ["Username or email already exists."]}), 409

    pwd_hash = hash_password(data["password"])
    role = data.get("role", "citizen")
    # For safety, default to citizen unless specified
    if role not in ["citizen", "admin"]:
        role = "citizen"

    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name, phone, role)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (data["username"], data["email"], pwd_hash, data["full_name"], data.get("phone", ""), role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "success": True,
            "message": "User registered successfully.",
            "user": {
                "id": user_id,
                "username": data["username"],
                "email": data["email"],
                "full_name": data["full_name"],
                "role": role
            }
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "errors": [str(e)]}), 500

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({"success": False, "errors": ["Username and password are required."]}), 400

    pwd_hash = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, email, password_hash, full_name, phone, role
        FROM users WHERE username = ? OR email = ?
        """,
        (username, username)
    )
    user = cursor.fetchone()
    conn.close()

    if not user or user["password_hash"] != pwd_hash:
        return jsonify({"success": False, "errors": ["Invalid credentials. Please verify your username and password."]}), 401

    # Automatically feed fresh real-time incident records for Vijay Nagar Square Corridor on each user login
    new_feed_records = []
    try:
        new_feed_records = auto_feed_accidents(count=random.randint(1, 2))
    except Exception as feed_err:
        print(f"[!] Auto-feed on login note: {feed_err}")

    return jsonify({
        "success": True,
        "message": f"Welcome back, {user['full_name']}! Live Vijay Nagar traffic data synchronized.",
        "new_data_feed_count": len(new_feed_records),
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "phone": user["phone"]
        }
    })

# ============================================================================
# ACCIDENT MANAGEMENT ENDPOINTS (Step 2, 3, 4, 5, 7)
# ============================================================================

@app.route("/api/accidents", methods=["GET"])
def get_accidents():
    """Retrieve accident records with optional filters (severity, status, search keyword)."""
    severity = request.args.get("severity")
    status = request.args.get("status")
    search = request.args.get("search")

    query = "SELECT * FROM accidents WHERE 1=1"
    params = []

    if severity and severity.lower() != "all":
        query += " AND severity = ?"
        params.append(severity)

    if status and status.lower() != "all":
        query += " AND status = ?"
        params.append(status)

    if search:
        search_pattern = f"%{search}%"
        query += " AND (title LIKE ? OR location_name LIKE ? OR landmark LIKE ? OR possible_cause LIKE ?)"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    query += " ORDER BY accident_date DESC, accident_time DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    accidents = [dict(row) for row in rows]
    return jsonify({"success": True, "count": len(accidents), "data": accidents})

@app.route("/api/accidents/<int:accident_id>", methods=["GET"])
def get_accident(accident_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accidents WHERE id = ?", (accident_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"success": False, "message": "Accident report not found."}), 404

    return jsonify({"success": True, "data": dict(row)})

@app.route("/api/accidents", methods=["POST"])
def create_accident():
    """Step 2: Accident Reporting & Step 3: Data Validation & Step 4: Database Storage"""
    data = request.get_json() or {}
    is_valid, errors = validate_accident_data(data)
    if not is_valid:
        return jsonify({"success": False, "errors": errors}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO accidents (
                title, location_name, landmark, latitude, longitude,
                accident_date, accident_time, severity, vehicle_type,
                road_condition, weather_condition, casualties_count,
                injuries_count, description, possible_cause, reported_by_id,
                reporter_name, reporter_contact, status, photo_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data["location_name"],
                data.get("landmark", ""),
                float(data["latitude"]),
                float(data["longitude"]),
                data["accident_date"],
                data["accident_time"],
                data["severity"],
                data.get("vehicle_type", "Four-Wheeler / Car"),
                data.get("road_condition", "Dry & Normal"),
                data.get("weather_condition", "Clear / Sunny"),
                int(data.get("casualties_count", 0)),
                int(data.get("injuries_count", 0)),
                data.get("description", ""),
                data.get("possible_cause", "Over-speeding"),
                data.get("reported_by_id"),
                data.get("reporter_name", "Anonymous Reporter"),
                data.get("reporter_contact", ""),
                "Pending",
                data.get("photo_url", "")
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM accidents WHERE id = ?", (new_id,))
        new_record = dict(cursor.fetchone())
        conn.close()

        return jsonify({
            "success": True,
            "message": "Accident report submitted successfully. Stored in SQL database with 'Pending' verification status.",
            "data": new_record
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "errors": [str(e)]}), 500

@app.route("/api/accidents/<int:accident_id>/status", methods=["PUT"])
def update_accident_status(accident_id):
    """Step 5: Accident Management (Admin feature to verify, update status, and add action notes)."""
    data = request.get_json() or {}
    new_status = data.get("status")
    admin_notes = data.get("admin_notes")
    action_taken = data.get("action_taken")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM accidents WHERE id = ?", (accident_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "Accident record not found."}), 404

    cursor.execute(
        """
        UPDATE accidents
        SET status = COALESCE(?, status),
            admin_notes = COALESCE(?, admin_notes),
            action_taken = COALESCE(?, action_taken),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (new_status, admin_notes, action_taken, accident_id)
    )
    conn.commit()

    cursor.execute("SELECT * FROM accidents WHERE id = ?", (accident_id,))
    updated_record = dict(cursor.fetchone())
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Accident report #{accident_id} updated successfully.",
        "data": updated_record
    })

@app.route("/api/accidents/<int:accident_id>", methods=["DELETE"])
def delete_accident(accident_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accidents WHERE id = ?", (accident_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"Accident #{accident_id} deleted."})

# ============================================================================
# HOTSPOT IDENTIFICATION & MAP VISUALIZATION ENGINE
# ============================================================================

@app.route("/api/hotspots", methods=["GET"])
def get_hotspots():
    """Identifies and groups accident-prone locations / blackspots using spatial clustering."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accidents")
    rows = cursor.fetchall()
    conn.close()

    accidents = [dict(r) for r in rows]
    hotspots = compute_hotspots(accidents)

    return jsonify({
        "success": True,
        "count": len(hotspots),
        "data": hotspots
    })

# ============================================================================
# AUTOMATED DATA FEEDING ENGINE (Guide Requirement: Auto-feed in single city)
# ============================================================================

@app.route("/api/feed/study-area", methods=["GET"])
def get_study_area():
    """Returns the designated single place / study area."""
    return jsonify({
        "success": True,
        "study_area": DESIGNATED_STUDY_AREA,
        "center": {"lat": 22.7555, "lng": 75.8955},
        "description": "Comprehensive road safety and blackspot analysis centered on Vijay Nagar Square & Bombay Hospital Corridor, Indore (M.P.)."
    })

@app.route("/api/feed/auto-generate", methods=["POST"])
def auto_generate_feed():
    """Automatically generates and injects simulated accidents into the Vijay Nagar - Bombay Hospital corridor."""
    data = request.get_json() or {}
    count = int(data.get("count", 1))
    if count < 1 or count > 50:
        count = 1

    try:
        new_records = auto_feed_accidents(count=count)
        return jsonify({
            "success": True,
            "message": f"Successfully fed {len(new_records)} automated accident record(s) into {DESIGNATED_STUDY_AREA}.",
            "count": len(new_records),
            "data": new_records
        })
    except Exception as e:
        return jsonify({"success": False, "errors": [str(e)]}), 500

@app.route("/api/feed/reset", methods=["POST"])
def reset_feed():
    """Resets database back to clean baseline seed data for Vijay Nagar - Bombay Hospital corridor."""
    try:
        init_db(force=True)
        return jsonify({
            "success": True,
            "message": f"Database reset to {DESIGNATED_STUDY_AREA} baseline dataset successfully."
        })
    except Exception as e:
        return jsonify({"success": False, "errors": [str(e)]}), 500

# ============================================================================
# FREE OPEN API AUTOMATED DATA GENERATION ENGINE
# (Fetches real road nodes from OpenStreetMap & live weather from Open-Meteo)
# ============================================================================

@app.route("/api/accidents/generate-from-api", methods=["POST"])
def generate_accidents_from_api_endpoint():
    """
    Automatically generates and populates realistic past accident datasets
    for Vijay Nagar Square using free public OpenStreetMap GIS & Open-Meteo weather APIs.
    """
    data = request.get_json() or {}
    count = int(data.get("count", 15))
    clear_existing = bool(data.get("clear_existing", True))

    if count < 1 or count > 50:
        count = 15

    try:
        records = generate_accidents_from_open_api(count=count, clear_existing=clear_existing)
        return jsonify({
            "success": True,
            "message": f"Successfully generated {len(records)} accident records for Vijay Nagar Square via Free Open API pipeline (OpenStreetMap + Open-Meteo).",
            "count": len(records),
            "api_sources": [
                "OpenStreetMap (OSM) Public Geographic Data",
                "Open-Meteo Free Public Weather API"
            ],
            "data": records
        })
    except Exception as e:
        return jsonify({"success": False, "errors": [str(e)]}), 500

@app.route("/api/accidents/open-api-status", methods=["GET"])
def get_open_api_status():
    """Returns connection and meteorological metadata from the free open APIs."""
    weather = fetch_open_meteo_weather()
    osm = fetch_osm_geographic_nodes()
    return jsonify({
        "success": True,
        "location": "Vijay Nagar Square, Indore",
        "coordinates": {"latitude": 22.7533, "longitude": 75.8937},
        "apis": {
            "gis": osm,
            "weather": weather
        }
    })

# ============================================================================
# ANALYTICS & STATISTICAL INSIGHTS
# ============================================================================

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Aggregate statistics for executive summaries, charts, and guide viva."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total counts
    cursor.execute("SELECT COUNT(*) FROM accidents")
    total_accidents = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(casualties_count), 0) FROM accidents")
    total_fatalities = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(injuries_count), 0) FROM accidents")
    total_injuries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM accidents WHERE status = 'Resolved'")
    total_resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM accidents WHERE status = 'Pending'")
    total_pending = cursor.fetchone()[0]

    # Severity distribution
    cursor.execute("SELECT severity, COUNT(*) as count FROM accidents GROUP BY severity")
    severity_breakdown = {row["severity"]: row["count"] for row in cursor.fetchall()}

    # Road condition distribution
    cursor.execute("SELECT road_condition, COUNT(*) as count FROM accidents GROUP BY road_condition")
    road_condition_breakdown = {row["road_condition"]: row["count"] for row in cursor.fetchall()}

    # Vehicle type distribution
    cursor.execute("SELECT vehicle_type, COUNT(*) as count FROM accidents GROUP BY vehicle_type")
    vehicle_breakdown = {row["vehicle_type"]: row["count"] for row in cursor.fetchall()}

    # Primary cause distribution
    cursor.execute("SELECT possible_cause, COUNT(*) as count FROM accidents GROUP BY possible_cause")
    cause_breakdown = {row["possible_cause"]: row["count"] for row in cursor.fetchall()}

    # Monthly distribution (last 6-12 months)
    cursor.execute("""
        SELECT strftime('%Y-%m', accident_date) as month, COUNT(*) as count
        FROM accidents
        GROUP BY month
        ORDER BY month ASC
    """)
    monthly_trend = [{"month": row["month"], "count": row["count"]} for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        "success": True,
        "summary": {
            "total_accidents": total_accidents,
            "total_fatalities": total_fatalities,
            "total_injuries": total_injuries,
            "total_resolved": total_resolved,
            "total_pending": total_pending
        },
        "severity_breakdown": severity_breakdown,
        "road_condition_breakdown": road_condition_breakdown,
        "vehicle_breakdown": vehicle_breakdown,
        "cause_breakdown": cause_breakdown,
        "monthly_trend": monthly_trend
    })

# ============================================================================
# ROAD SAFETY INFORMATION (Step 6) & EMERGENCY CONTACTS
# ============================================================================

@app.route("/api/traffic-rules", methods=["GET"])
def get_traffic_rules():
    category = request.args.get("category")
    conn = get_db_connection()
    cursor = conn.cursor()

    if category and category.lower() != "all":
        cursor.execute("SELECT * FROM traffic_rules WHERE category = ? ORDER BY id", (category,))
    else:
        cursor.execute("SELECT * FROM traffic_rules ORDER BY category, id")

    rows = cursor.fetchall()
    conn.close()

    rules = [dict(r) for r in rows]
    return jsonify({"success": True, "count": len(rules), "data": rules})

@app.route("/api/emergency-contacts", methods=["GET"])
def get_emergency_contacts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emergency_contacts ORDER BY id")
    rows = cursor.fetchall()
    conn.close()

    contacts = [dict(r) for r in rows]
    return jsonify({"success": True, "count": len(contacts), "data": contacts})

# ============================================================================
# STATIC FRONTEND SERVING
# ============================================================================

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if FRONTEND_DIST and os.path.exists(FRONTEND_DIST):
        if path != "" and os.path.exists(os.path.join(FRONTEND_DIST, path)):
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, "index.html")
    return jsonify({
        "system": "Road Safety Management and Analysis System API",
        "status": "Online",
        "endpoints": [
            "/api/accidents",
            "/api/hotspots",
            "/api/analytics",
            "/api/traffic-rules",
            "/api/emergency-contacts",
            "/api/auth/login",
            "/api/auth/register"
        ]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Road Safety Management System Server running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
