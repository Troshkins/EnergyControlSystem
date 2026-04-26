# Energy Control System

The system receives electricity prices, demand forecasts, asset constraints, and intraday updates, then creates a cost-minimizing energy schedule.

## Tech Stack

- Backend: Python, FastAPI
- Optimization: Google OR-Tools
- Database: PostgreSQL
- Event streaming: Apache Kafka
- Frontend: React, Vite, Recharts
- Local deployment: Docker Compose

## Main Components

### Data Ingestion Service

The ingestion service accepts and validates input data:

- hourly electricity prices
- demand forecasts
- energy asset constraints
- intraday demand updates

### Optimization Service

The optimization service builds a 24-hour day-ahead schedule. It decides how much energy should come from:

- grid electricity
- gas
- battery discharge

It also decides when the battery should be charged. The objective is to minimize total energy cost while satisfying demand and respecting operational constraints.

Main constraints:

- demand must be covered every hour
- battery state of charge must stay between 0 and capacity
- max charge and discharge limits must be respected
- gas output must not exceed its maximum capacity
- the battery cannot charge and discharge at the same time

### Intraday Service

The intraday service simulates real-time correction during the operating day. It receives updated actual demand, compares it with the day-ahead schedule, calculates the deviation, and creates a corrective action.

The service stores intraday actions in PostgreSQL and publishes them to Kafka.

### Visualization Layer

The React dashboard displays:

- input data
- day-ahead schedule
- battery state of charge
- intraday corrections
- test scenario results

## Kafka Topics

- `price_signals`
- `demand_forecasts`
- `ecs_schedule`
- `intraday_updates`
- `intraday_actions`

## API Endpoints

### Ingestion Service

- `POST /prices`
- `POST /forecast`
- `POST /assets`
- `POST /intraday`
- `GET /prices`
- `GET /forecast`
- `GET /assets`
- `GET /intraday`
- `GET /health`

### Optimization Service

- `POST /optimize/day-ahead`
- `GET /schedule/{date}`
- `GET /health`

### Intraday Service

- `POST /optimize/intraday`
- `GET /intraday/actions/{date}`
- `GET /health`

## Database Tables

- `prices`
- `demand_forecasts`
- `energy_assets`
- `day_ahead_schedules`
- `intraday_actions`
- `simulation_runs`
- `test_results`

## Running Locally

Create a local environment file:

```bash
cp .env.example .env
