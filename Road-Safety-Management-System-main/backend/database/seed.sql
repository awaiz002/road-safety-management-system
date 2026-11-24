-- Road Safety Management System - Initial Seed Data
-- FOCUSED ON SINGLE LOCATION: Vijay Nagar Square, Indore, Madhya Pradesh

-- 1. Default Users (Admin and Citizens)
-- Password for all seed users is 'admin123' or 'user123' (SHA256 hashed)
-- admin123 sha256: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- user123 sha256: e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446

INSERT INTO users (username, email, password_hash, full_name, phone, role) VALUES
('admin', 'admin@roadsafety.indore.gov.in', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Indore Traffic Administrator', '+91 731 2522222', 'admin'),
('rahul_sharma', 'rahul@example.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'Rahul Sharma (Indore)', '+91 98260 11223', 'citizen'),
('priya_patel', 'priya@example.com', 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', 'Priya Patel (Indore)', '+91 98265 33445', 'citizen');

-- 2. Base Traffic Rules and Road Signs (Compliant with Motor Vehicles Act & Indore Traffic Police)
INSERT INTO traffic_rules (category, title, code, description, fine_amount, icon_type, importance) VALUES
('Mandatory Signs', 'Stop Sign', 'M-01', 'Octagonal red sign. Drivers MUST bring vehicle to full stop at Vijay Nagar Square stop line before proceeding.', '₹1,000 - ₹2,000', 'stop', 'Critical'),
('Mandatory Signs', 'No Entry for Private Vehicles in BRTS Lane', 'M-02', 'Red circle with white horizontal bar. Private cars and bikes are strictly banned from AB Road BRTS lane.', '₹1,500 + Challan', 'no-entry', 'Critical'),
('Mandatory Signs', 'Speed Limit 40 km/h (Vijay Nagar Zone)', 'M-03', 'Circular white sign with red border. Max speed on AB Road commercial corridor is 40 km/h.', '₹2,000 (LMV) / ₹4,000 (HMV)', 'speed-50', 'Critical'),
('Mandatory Signs', 'Give Way / Yield', 'M-04', 'Inverted triangle sign. Yield right of way to vehicles already circulating inside Vijay Nagar square.', '₹1,000', 'yield', 'High'),
('Mandatory Signs', 'No U-Turn at Vijay Nagar Square', 'M-05', 'U-turn prohibited at main square to prevent gridlock. Use designated U-turn cuts 200m ahead.', '₹1,000', 'no-overtake', 'High'),
('Cautionary Signs', 'Pedestrian Crossing (Mall Corridor Ahead)', 'C-01', 'Cautionary sign near C21 and Malhar Mega Mall. Motorists must reduce speed for shoppers crossing.', '₹1,000', 'pedestrian', 'High'),
('Cautionary Signs', 'Hospital Ambulance Zone Ahead', 'C-02', 'Cautionary sign on Scheme 54 road near Bombay Hospital. Give immediate clearance to emergency sirens.', '₹1,000', 'school', 'Critical'),
('Cautionary Signs', 'Sharp Rotary Curve Ahead', 'C-03', 'Warning of sharp rotary curvature approaching Radisson Square from Vijay Nagar.', 'Warning', 'sharp-left', 'Medium'),
('Cautionary Signs', 'Slippery Surface During Monsoon', 'C-04', 'Warning sign indicating road surface prone to skidding near Meghdoot Garden crossing.', 'Warning', 'slippery', 'High'),
('Cautionary Signs', 'Heavy Freight Merge on MR-10', 'C-05', 'Warning of heavy freight vehicles merging onto arterial road from MR-10 bypass.', 'Warning', 'narrow-bridge', 'Medium'),
('Traffic Rules & Penalties', 'Drunken Driving / Under the Influence (Section 185)', 'R-01', 'Zero tolerance breathalyzer testing across Vijay Nagar nightlife & lounge zone.', '₹10,000 + Court Challan / Suspension', 'drunk-driving', 'Critical'),
('Traffic Rules & Penalties', 'Mandatory ISI Helmet for Rider & Pillion (Section 129)', 'R-02', 'Both rider and pillion on two-wheelers must wear secured ISI helmet across Indore city roads.', '₹1,000', 'helmet', 'Critical'),
('Traffic Rules & Penalties', 'Seat Belt Rule (Section 138(3))', 'R-03', 'All occupants of four-wheelers must wear three-point seat belts at all times.', '₹1,000', 'seatbelt', 'Critical'),
('Traffic Rules & Penalties', 'Mobile Phone Usage While Driving (Section 184)', 'R-04', 'Operating handheld mobile phone while driving on AB Road / Vijay Nagar corridor.', '₹1,000 - ₹5,000', 'phone-drive', 'Critical');

-- 4. Emergency Contacts Directory (Indore & Vijay Nagar Specific)
INSERT INTO emergency_contacts (service_name, category, contact_number, description, available_hours, region) VALUES
('Madhya Pradesh Dial 100 / 112', 'National Helpline', '112', 'Integrated Police, Ambulance, and Fire emergency response across Indore.', '24x7', 'Indore / M.P.'),
('Vijay Nagar Police Station', 'Police & Patrol', '0731-2550100', 'Local jurisdiction police station for Vijay Nagar Square and Scheme 54.', '24x7', 'Vijay Nagar, Indore'),
('Indore Police Control Room', 'Police & Patrol', '0731-2522222', 'Centralized police control room for rapid squad dispatch and accident investigation.', '24x7', 'Indore City'),
('Indore Traffic Police Helpline & WhatsApp', 'Police & Patrol', '7049122222', 'Direct helpline for traffic jams, breakdown towing, and accident rescue.', '24x7', 'Indore Urban'),
('State Medical Ambulance (EMRI)', 'Ambulance & Medical', '108', 'Free government emergency ambulance dispatch with trained paramedical staff.', '24x7', 'Indore / M.P.'),
('Bombay Hospital Indore (Emergency / Trauma)', 'Ambulance & Medical', '0731-4771111', 'Multi-specialty emergency trauma and ICU center located 500m from Vijay Nagar Square.', '24x7', 'Scheme 54, Vijay Nagar'),
('MY Hospital Apex Trauma Center Indore', 'Ambulance & Medical', '0731-2527383', 'Largest government apex polytrauma care hospital in Indore region.', '24x7', 'Indore'),
('National Highway Helpline (NHAI - Indore Bypass)', 'Highway Helpline', '1033', 'Towing, medical rescue, and emergency assistance along Indore-Bhopal & AB Bypass.', '24x7', 'Indore Highways');
