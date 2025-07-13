# 1. Overview

The **Sensor Node** is a client application that simulates a remote device generating and transmitting telemetry data. It is designed for resilience and continued operation even in the face of network instability.

### Key Features

- **Data Generation**  
  Creates mock sensor data (`name`, `value`, `timestamp`) at a configurable rate.

- **Persistent Buffering**  
  Uses a local SQLite database to save every message it generates. This ensures no data is lost if the application crashes or the network is down.

- **Asynchronous Retries**  
  A dedicated background service automatically retries sending messages that failed their initial delivery attempt.

- **Exponential Backoff**  
  The retry mechanism uses an exponential backoff strategy with jitter to avoid overwhelming the sink after a network outage.

- **Configuration Driven**  
  All behavior (sensor name, rate, sink address, retry logic) is controlled via the central `config.ini` file.

# 2. Architecture

The Sensor Node uses a multi-service `asyncio` architecture to separate concerns and maximize throughput:

### Components

- **SensorService**  
  The primary service responsible for generating new sensor data at the configured rate and making the initial attempt to send it via the HTTP client.

- **RetryService**  
  A background service that periodically queries the local database for messages marked as **FAILED**, then attempts to re-send them according to the configured backoff strategy.

- **SensorDataSQLRepository**  
  An adapter that provides a clean interface to the local SQLite database, abstracting away all SQL queries and schema details. I choose SQLite for its simplicity and to save time, in real world applications, different db or probably NoSql solutions could be used.

- **AsyncHttpTelemetryClient**  
  An adapter that handles the actual HTTP communication with the Telemetry Sink (POSTing JSON payloads, handling errors, etc.).

---

With this design, **data generation** is never blocked by slow network I/O or retry attempts—ensuring high availability and “at-most-once” delivery semantics in the face of failures.```


