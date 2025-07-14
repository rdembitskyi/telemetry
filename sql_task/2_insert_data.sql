-- Clear existing data to ensure a clean test run.
TRUNCATE TABLE rooms, sensors, sensor_data RESTART IDENTITY;

-- Insert Rooms
INSERT INTO rooms (room_name) VALUES ('room_A'), ('room_B');

-- Insert Sensors for room_A (1 for V, 2 for R)
INSERT INTO sensors (sensor_name, sensor_type, room_id) VALUES
    ('sensor_A_V1', 'V', (SELECT room_id FROM rooms WHERE room_name = 'room_A')),
    ('sensor_A_R1', 'R', (SELECT room_id FROM rooms WHERE room_name = 'room_A')),
    ('sensor_A_R2', 'R', (SELECT room_id FROM rooms WHERE room_name = 'room_A'));

-- Insert Sensors for room_B (2 for V, 3 for R)
INSERT INTO sensors (sensor_name, sensor_type, room_id) VALUES
    ('sensor_B_V1', 'V', (SELECT room_id FROM rooms WHERE room_name = 'room_B')),
    ('sensor_B_V2', 'V', (SELECT room_id FROM rooms WHERE room_name = 'room_B')),
    ('sensor_B_R1', 'R', (SELECT room_id FROM rooms WHERE room_name = 'room_B')),
    ('sensor_B_R2', 'R', (SELECT room_id FROM rooms WHERE room_name = 'room_B')),
    ('sensor_B_R3', 'R', (SELECT room_id FROM rooms WHERE room_name = 'room_B'));

-- Insert Sensor Data
INSERT INTO sensor_data (sensor_id, value, timestamp) VALUES
    -- Scenario: Normal measurements for room_A at 10:00:00
    -- All sensors (1 V, 2 R) report data with slightly different timestamps.
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_A_V1'), 120.5, '2025-07-13 10:00:00.100123'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_A_R1'), 12.1,  '2025-07-13 10:00:00.200456'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_A_R2'), 11.9,  '2025-07-13 10:00:00.300789'),

    -- Scenario: Normal measurements for room_B at 10:00:00
    -- Both V sensors and all three R sensors report data.
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_V1'), 240.8, '2025-07-13 10:00:00.150111'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_V2'), 239.2, '2025-07-13 10:00:00.250222'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_R1'), 25.0,  '2025-07-13 10:00:00.350333'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_R2'), 24.5,  '2025-07-13 10:00:00.450444'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_R3'), 25.5,  '2025-07-13 10:00:00.550555'),

    -- Scenario (c): No measurement from one sensor in a room for a given second.
    -- For room_A at 10:00:01, only R1 sensor sends data. R2 sensor does not report.
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_A_R1'), 12.0,  '2025-07-13 10:00:01.100000'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_A_V1'), 120.6, '2025-07-13 10:00:01.100000'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_A_R1'), 12.2,  '2025-07-13 10:00:01.200000'),

    -- Scenario (d): Measurement for R but no measurement for V.
    -- For room_B at 10:00:02, only the R sensors report data.
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_R1'), 25.1, '2025-07-13 10:00:02.300000'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_R2'), 24.6, '2025-07-13 10:00:02.400000'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_R3'), 25.6, '2025-07-13 10:00:02.500000'),
    -- Note: No V sensors from room_B report at this time.

    -- Scenario (d inverse): Measurement for V but no measurement for R.
    -- For room_B at 10:00:03, only the V sensors report data.
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_V1'), 241.0, '2025-07-13 10:00:03.100000'),
    ((SELECT sensor_id FROM sensors WHERE sensor_name = 'sensor_B_V2'), 238.8, '2025-07-13 10:00:03.200000');