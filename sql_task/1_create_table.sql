-- Drop tables if they exist to ensure a clean slate for testing.
DROP TABLE IF EXISTS readings;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS rooms;

-- Create a custom ENUM type for sensor values.
-- This ensures that the sensor_type can only be 'V' or 'R'.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sensor_type_enum') THEN
        CREATE TYPE sensor_type_enum AS ENUM ('V', 'R');
    END IF;
END$$;


-- Table for storing room information.
CREATE TABLE rooms (
    room_id   SERIAL PRIMARY KEY,
    room_name VARCHAR(255) NOT NULL UNIQUE
);

-- Table for storing sensor information.
CREATE TABLE sensors (
    sensor_id   SERIAL PRIMARY KEY,
    sensor_name VARCHAR(255) NOT NULL UNIQUE,
    sensor_type sensor_type_enum NOT NULL,
    room_id     INTEGER NOT NULL,

    -- Establish a foreign key relationship to the rooms table.
    -- ON DELETE CASCADE means if a room is deleted, all its sensors are also deleted.
    CONSTRAINT fk_room
        FOREIGN KEY(room_id)
        REFERENCES rooms(room_id)
        ON DELETE CASCADE
);

-- Table for storing telemetry data from sensors.
CREATE TABLE sensor_data (
    sensor_data_id  BIGSERIAL PRIMARY KEY,
    sensor_id   INTEGER NOT NULL,
    value       DOUBLE PRECISION NOT NULL, -- Using DOUBLE for floating point values.
    timestamp   TIMESTAMP(6) NOT NULL,     -- Timestamp with microsecond precision.

    -- Establish a foreign key relationship to the sensors table.
    CONSTRAINT fk_sensor
        FOREIGN KEY(sensor_id)
        REFERENCES sensors(sensor_id)
        ON DELETE CASCADE
);

-- An index on sensor_id and timestamp can significantly improve query performance,
-- as we will be joining on sensor_id and filtering/grouping by timestamp.
CREATE INDEX idx_readings_sensor_id_timestamp ON sensor_data (sensor_id, timestamp);
CREATE INDEX idx_readings_timestamp ON sensor_data (timestamp);