# DavaX Python Project

This repository contains a multi-service Python project for mathematical operations and logging, designed with microservices architecture and Docker support.

## Project Structure

- `math-api/`: Main API service for mathematical operations (e.g., power calculation), health checks, and request logging.
- `logger-microservice/`: Microservice for logging requests and events.
- `shared_core/`: Shared library for configuration, database, dependency injection, Kafka messaging, and models.
- `docker-compose.yml`: Docker Compose file to orchestrate all services.

## Features

- **RESTful API for Mathematical Operations**  
  Built with [FastAPI](https://fastapi.tiangolo.com/) for high performance and modern Pythonic development, exposing endpoints for core math operations (such as power calculation).

- **Async Support**  
  All services are designed with asynchronous execution in mind for efficient, non-blocking operations.

- **Health Check Endpoints**  
  Both the `math-api` and `logger-microservice` include health endpoints.

- **Request Logging Middleware**  
  Automatically logs all incoming requests and important events for traceability and easier debugging.

- **API Key Security**  
  Endpoints are protected using API keys sent in the request header; keys are validated against entries stored in the database.

- **Kafka Integration for Log Dispatching**  
  Publishes logs and events to Kafka topics for real-time log streaming

- **Oracle Database Support**  
  Connects to Oracle databases for persistent api keys and logs.

- **Custom Dependency Injection Container**  
  Implements a custom DI container to manage long-lived resources—such as database connections and Kafka producers/consumers—beyond what FastAPI’s built-in dependency system offers.

- **Dockerized Services for Easy Deployment**  
  All services are containerized and orchestrated with Docker Compose for quick setup and scalable deployments in any environment.


## Getting Started

### Prerequisites
- Python 3.8+
- Docker & Docker Compose

### Installation
1. Clone the repository:
   ```sh
   git clone <repo-url>
   ```
2. Install dependencies for each service:
   ```sh
   pip install -r math-api/requirements.txt
   pip install -r logger-microservice/requirements.txt
   ```

### Running with Docker Compose

Start all services with a single command:

```sh
docker-compose up --build
```

### Running Locally
Run the main API:
```sh
python -m uvicorn main:app --port 8000
```
Run the logger microservice:
```sh
python -m uvicorn main:app --port 8001
```
## Configuration
- **Environment Variables:**  
  Each service (`math-api`, `logger-microservice`) has its own environment file for configuration.

  - When running **locally**, use a `.env` file in each service’s directory:
    - `math-api/.env`
    - `logger-microservice/.env`
  - When running with **Docker Compose**, use a `.env.container` file in each service’s directory:
    - `math-api/.env.container`
    - `logger-microservice/.env.container`

- **How It Works:**  
  The application loads configuration values (e.g., `KAFKA_BROKER_URL`, `ORACLE_DB_CONN`, `API_KEY`) from the respective `.env` or `.env.container` files, depending on your environment.

- **Config Code:**  
  Configuration logic and defaults are managed in:
    - `shared_core/config/`
    - `math-api/infrastructure/config.py`

## Environment Variables

Each service requires its own environment file.  
For local development, use a `.env` file in each service directory.  
For Docker deployments, use `.env.container` in each service directory.

```env
# Common variables (used by both services)
DB_USER=user                     # Oracle DB username
DB_PASSWORD=strongpass           # Oracle DB password
DB_DSN=localhost/xepdb1          # Oracle DB DSN (Data Source Name)
KAFKA_BOOTSTRAP_SERVERS=kafka:9092 # Kafka server address (host:port)

# Only for math-api
KAFKA_REQUEST_TIMEOUT_MS=2000    # Kafka request timeout in milliseconds
SVC_HOST=api01                   # Hostname for the math-api service, used for logging
SVC_NAME=math-api                # Service name (default: math-api), used for logging
```

## API Endpoints

Below are the available endpoints in the `math-api` service.

### Math Endpoints

- **POST `/math/pow`**  
  Calculate the result of raising a base to a given exponent.
  - **Request Body:**  
    ```json
    {
      "base": 2,
      "exponent": 3
    }
    ```
  - **Response Example:**  
    ```json
    {
      "base": 2,
      "exponent": 3,
      "result": 8
    }
    ```

- **GET `/math/fibo/{n}`**  
  Calculate the first `n` Fibonacci numbers.
  - **Example Request:**  
    ```
    GET /math/fibo/7
    ```
  - **Response Example:**  
    ```json
    {
      "n": 7,
      "result": 13
    }
    ```

- **GET `/math/factorial/{number}`**  
  Calculate the factorial of a given number.
  - **Example Request:**  
    ```
    GET /math/factorial/5
    ```
  - **Response Example:**  
    ```json
    {
      "number": 5,
      "result": 120
    }
    ```

---

### Health Endpoint

- **GET `/health`**  
  Returns service health status.
  - **Response Example:**  
    ```json
    {
      "status": "DEGRADED",
        "details": {
          "db": {
            "status": "UP"
          },
          "kafka": {
            "status": "DOWN"
          },
          "log_microservice": {
            "status": "DOWN"
          }
        }
    }
    ```

---

## Request & Logging Flow

This section describes how an incoming request is processed and logged throughout the DavaX microservices architecture, ensuring both results and traceability for every operation.

### Overview

The DavaX system consists of two primary services—`math-api` and `logger-microservice`—that interact via Kafka and a shared OracleDB for robust processing and logging. Every client request triggers a series of coordinated steps for security, calculation, persistence, and logging.

---

### Step-by-Step Request Flow

1. **Client** sends a request to the `math-api` service (for operations such as power, Fibonacci, or factorial calculations).
2. **math-api**:
    - **Validates** the API key by querying OracleDB.
    - **Performs** the requested mathematical operation.
    - **Persists** a record of the request (including input parameters) directly to OracleDB.
    - **Sends logs/events** asynchronously to Kafka, targeting the logger microservice.
3. **logger-microservice**:
    - **Receives logs/events** from Kafka.
    - **Saves** these logs into OracleDB.
4. **math-api** returns the final response to the client.

---

### Sequence Diagram

```mermaid
sequenceDiagram
    participant Client
    participant MathAPI as math-api
    participant OracleDB
    participant Kafka
    participant Logger as logger-microservice

    Client->>MathAPI: API Request (e.g. /math/pow)
    MathAPI->>OracleDB: Validate API Key
    MathAPI->>MathAPI: Perform Calculation
    MathAPI->>OracleDB: Save Request Record
    MathAPI->>Kafka: Send Log/Event
    Kafka->>Logger: Deliver Log/Event
    Logger->>OracleDB: Save Log Record
    MathAPI-->>Client: API Response