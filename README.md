# Telemetry System (Overall Project)

## 1. Project Overview

This project implements a simple, robust, and extensible telemetry system composed of two independent Python components:

- **Sensor Node** (`sensor_node/`):  
  A client application that simulates a remote device. It generates telemetry data at a configurable rate and sends it to the sink. It is designed to be resilient to network failures, with a local database for buffering and an automatic retry mechanism.

- **Telemetry Sink** (`telemetry_sink/`):  
  A server application that receives telemetry data from one or more sensor nodes. It is designed for high throughput and robustness, featuring rate limiting, in-memory buffering, and secure, encrypted logging of all received data.

The system is built with a protocol-agnostic core, allowing for future expansion to support communication protocols like gRPC in addition to the current HTTP/REST implementation.

## 2. Core Architectural Principles

This application is built on an **asyncio** stack and follows key architectural principles:

- **Separation of Concerns**  
  Each component has a well-defined responsibility. The Sensor Node handles data generation and initial transmission; the Telemetry Sink handles data reception and storage.

- **Modularity**  
  Within each component, services are broken down into logical units (e.g., API Adapters, Core Services, Domain Models), making the system easier to maintain, test, and extend.

- **Protocol Agnosticism**  
  The core business logic (rate limiting, buffering, logging, retries) is decoupled from the transport layer (HTTP), allowing new protocols like gRPC to be added without rewriting the core application.

- **Robustness and Resilience**  
  The system handles real-world failures: the Sensor Node buffers failed messages and retries them with exponential backoff, and the Sink handles backpressure via rate limiting and in-memory buffering.

- **Configuration Driven**  
  All key parameters (rates, addresses, buffer sizes, keys) are externalized to a central `config.ini` file, allowing behavior to be tuned without changing code.

## 3. Getting Started

### Prerequisites

- Python 3.12+  
- `pip` for package management

### Installation

It is highly recommended to use a virtual environment:

```bash
# 1. Clone the repository (or set up the project folder)
git clone <repository-url>
cd your-project-folder

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies for both components
pip install -r sensor_node/requirements.txt
pip install -r telemetry_sink/requirements.txt

# 4. Run the Sensor Node and Telemetry Sink
python -m sensor_node.main
python -m telemetry_sink.main
```

You would see logs indicating that the Sensor Node is generating and sending data, while the Telemetry Sink is receiving and processing it.


5. SQL Task could be find in sql_task directory.