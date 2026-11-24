-- Road Safety Management System - Database Schema (SQL)
-- Conforms to Project Synopsis Specifications

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    role TEXT NOT NULL DEFAULT 'citizen', -- 'citizen', 'admin'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    location_name TEXT NOT NULL,
    landmark TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    accident_date TEXT NOT NULL,
    accident_time TEXT NOT NULL,
    severity TEXT NOT NULL, -- 'Minor', 'Major', 'Fatal'
    vehicle_type TEXT NOT NULL, -- 'Two-Wheeler', 'Four-Wheeler / Car', 'Commercial Bus', 'Heavy Truck', 'Auto-Rickshaw', 'Pedestrian', 'Multiple Vehicles'
    road_condition TEXT NOT NULL, -- 'Dry & Normal', 'Wet / Waterlogged', 'Potholed & Damaged', 'Under Construction', 'Slippery / Oil Spill', 'Poor Street Lighting'
    weather_condition TEXT NOT NULL, -- 'Clear / Sunny', 'Rainy / Monsoon', 'Heavy Fog / Mist', 'Night / Dark', 'Stormy / Wind'
    casualties_count INTEGER DEFAULT 0,
    injuries_count INTEGER DEFAULT 0,
    description TEXT,
    possible_cause TEXT, -- 'Over-speeding', 'Drunk Driving', 'Signal Jump', 'Pothole / Road Defect', 'Brake Failure', 'Weather / Low Visibility', 'Distracted Driving'
    reported_by_id INTEGER,
    reporter_name TEXT,
    reporter_contact TEXT,
    status TEXT DEFAULT 'Pending', -- 'Pending', 'Verified', 'Under Investigation', 'Resolved', 'Rejected'
    admin_notes TEXT,
    action_taken TEXT,
    photo_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reported_by_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS traffic_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL, -- 'Mandatory Signs', 'Cautionary Signs', 'Informatory Signs', 'Traffic Rules & Penalties', 'Safety Guidelines'
    title TEXT NOT NULL,
    code TEXT,
    description TEXT NOT NULL,
    fine_amount TEXT,
    icon_type TEXT,
    importance TEXT DEFAULT 'High'
);

CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    category TEXT NOT NULL, -- 'National Helpline', 'Ambulance & Medical', 'Police & Patrol', 'Highway Helpline'
    contact_number TEXT NOT NULL,
    description TEXT,
    available_hours TEXT DEFAULT '24x7',
    region TEXT DEFAULT 'All India'
);

-- Indexes for performance and quick searches
CREATE INDEX IF NOT EXISTS idx_accidents_location ON accidents(location_name);
CREATE INDEX IF NOT EXISTS idx_accidents_severity ON accidents(severity);
CREATE INDEX IF NOT EXISTS idx_accidents_date ON accidents(accident_date);
CREATE INDEX IF NOT EXISTS idx_accidents_status ON accidents(status);
