WITH AggregatedValues AS (
    SELECT
        r.room_name,
        -- Group measurements into one-second buckets.
        DATE_TRUNC('second', sd.timestamp) AS time_bucket,

        -- Conditionally average the values based on sensor type.
        -- This pivots the V and R data into separate columns.
        AVG(CASE WHEN s.sensor_type = 'V' THEN sd.value ELSE NULL END) AS avg_v,
        AVG(CASE WHEN s.sensor_type = 'R' THEN sd.value ELSE NULL END) AS avg_r

    FROM
        sensor_data sd
    JOIN
        sensors s ON sd.sensor_id = s.sensor_id
    JOIN
        rooms r ON s.room_id = r.room_id
    GROUP BY
        r.room_name,
        time_bucket
)
SELECT
    av.room_name AS room,
    av.time_bucket AS timestamp,

    -- Calculate current I = V / R.
    -- Use NULLIF to prevent division-by-zero errors.
    -- If avg_v or avg_r is NULL, the result will correctly be NULL.
    (av.avg_v / NULLIF(av.avg_r, 0)) AS "I",

    av.avg_v AS "V",
    av.avg_r AS "R"
FROM
    AggregatedValues av
ORDER BY
    room,
    timestamp;