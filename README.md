# Receipt Processor

A web service that processes receipts and calculates points based on configurable rules.

## Features

- RESTful API built with FastAPI and Redis for in-memory storage.
- Dynamic points calculation based on configurable rules:
  - A sample of rules are provided in [config/rules.yaml](config/rules.yaml)
  - Rules can be updated in runtime via API endpoints.
  - [ReceiptProcessor](lib/core/receipt_processor.py) calculates points based on the rules.
- Points, receipts and rules are stored in Redis.
- Structured logging with contextual information.

## Running with Docker Compose

1. Build and start the services (run from the root directory):
```bash
docker compose -f docker-compose.yml up --build
```

2. Stop the services (run from the root directory):
```bash
docker compose -f docker-compose.yml down
```

The REST API will be available at http://127.0.0.1:5000

Swagger UI will be available at http://127.0.0.1:5000/docs

## API Endpoints

### Process Receipt
```http
POST /receipts/process
```
Process a receipt and calculate points.
- Request: Receipt JSON object
- Response: `{ "id": "receipt-uuid" }`
- Status Codes:
  - 200: Success
  - 400: Invalid receipt
  - 500: Server error

### Get Points
```http
GET /receipts/{id}/points
```
Get points for a processed receipt.
- Response: `{ "points": 100 }`
- Status Codes:
  - 200: Success
  - 404: Receipt not found
  - 500: Server error

### Rules Configuration
```http
GET /config/rules
PUT /config/rules
```
Get or update the rules configuration.
- GET Response: Current rules in YAML format
- PUT Request: YAML file with new rules
- Status Codes:
  - 200: Success
  - 400: Invalid rules format
  - 500: Server error

## Tech Stack

- **FastAPI**: Asynchronous web framework for building APIs
- **Redis**: In-memory data store
- **Pydantic**: Data validation using Python type annotations
- **Structlog**: Structured logging
- **PyYAML**: YAML configuration parsing
- **Docker & Docker Compose**: Containerization and orchestration
- **Poetry**: Python package management

## Development Setup

1. Install dependencies:
```bash
poetry install
```

2. Start Redis:
```bash
docker compose -f docker-compose.yml up redis-server -d
```

3. Start the API server:
```bash
poetry run uvicorn rest_server.main:server --host 0.0.0.0 --port 5000 --reload
```

## Example Receipt

```json
{
  "retailer": "Target",
  "purchaseDate": "2022-01-01",
  "purchaseTime": "13:01",
  "items": [
    {
      "shortDescription": "Mountain Dew 12PK",
      "price": "6.49"
    },
    {
      "shortDescription": "Emils Cheese Pizza",
      "price": "12.25"
    }
  ],
  "total": "18.74"
}
```

## Configuration

Rules are defined in `config/rules.yaml`. Example rules include:
- One point for each alphanumeric character in the retailer name
- 50 points if the total is a round dollar amount
- 25 points if the total is a multiple of 0.25
- 5 points for every two items on the receipt
- Points equal to 20% of the item price (rounded up) for items with descriptions of length divisible by 3
- 6 points if the day in the purchase date is odd
- 10 points if the time of purchase is between 2:00pm and 4:00pm

## Health Checks

The application includes health checks for both services:
- REST API: `GET /health`
- Redis: Periodic ping check

## Resource Limits

Docker containers are configured with the following resource limits:
- REST API: 1GB max, 512MB reserved
- Redis: 512MB max, 256MB reserved
