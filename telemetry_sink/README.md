# Telemetry Sink (`telemetry_sink/`)

## 1. Overview

The **Telemetry Sink** is a high-performance server application designed to receive, process, and securely store telemetry data from multiple sensor nodes.

### Key Features

- **High-Throughput API**  
  Uses **FastAPI** to provide a fast, asynchronous HTTP endpoint for data ingestion.

- **Rate Limiting**  
  Protects the service from being overwhelmed by enforcing a global “bytes per second” limit on incoming traffic.

- **In-Memory Buffering**  
  Decouples network requests from file I/O using an internal `asyncio.Queue`. This keeps the API responsive while data is written to disk in efficient batches.

- **Timed & Sized Batching**  
  Flushes buffered messages to the log file when either a configured batch size is reached or a timeout occurs—balancing throughput and freshness.

- **Encrypted-at-Rest**  
  Encrypts every log entry with **Fernet (AES-128)** before writing to disk, ensuring data confidentiality.

- **Configuration Driven**  
  All parameters (bind address, buffer sizes, rate limits, encryption key) are controlled via the central `config.ini` file.

---

## 2. Architecture

The Telemetry Sink is implemented as an **asyncio**-based pipeline with clear separation of concerns:

- **API Adapter (`http_server.py`)**  
  A FastAPI application that exposes the `/telemetry` endpoint.  
  - Validates incoming JSON payloads  

- **TelemetryService**  
  The core orchestration layer, responsible for:  
  - Coordinating rate limiting and buffering  
  - Exposing a transport-agnostic interface for message ingestion

- **RateLimiter**  
  Enforces a strict “bytes per second” budget across all incoming requests, dropping or delaying excess traffic.

- **BufferManager**  
  A thin wrapper over an `asyncio.Queue` that holds messages in memory until they’re ready to be batched.

- **LogWriter**  
  A background “timed-batch consumer” that:  
  1. Flushes messages from the buffer based on size or timeout
  2. Encrypts each record via the CryptoService  
  3. Appends the batch to the on-disk log file

- **CryptoService**  
  A utility wrapper around the **cryptography** library’s Fernet API, handling encryption and decryption of log messages.  
