CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    price NUMERIC NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS demand_forecasts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    demand NUMERIC NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS energy_assets (
    id SERIAL PRIMARY KEY,
    asset_type VARCHAR(50) NOT NULL, -- grid / gas / battery
    max_output NUMERIC,
    capacity NUMERIC,
    max_charge NUMERIC,
    max_discharge NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS day_ahead_schedules (
    id SERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    schedule_date DATE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    hour INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    demand NUMERIC NOT NULL,
    grid_usage NUMERIC NOT NULL,
    gas_usage NUMERIC NOT NULL,
    battery_charge NUMERIC NOT NULL,
    battery_discharge NUMERIC NOT NULL,
    battery_soc NUMERIC NOT NULL,
    hour_cost NUMERIC NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intraday_actions (
    id SERIAL PRIMARY KEY,
    run_id UUID,
    action_date DATE NOT NULL DEFAULT CURRENT_DATE,
    timestamp TIMESTAMP NOT NULL,
    hour INTEGER NOT NULL DEFAULT 0,
    planned_demand NUMERIC,
    actual_demand NUMERIC NOT NULL DEFAULT 0,
    deviation NUMERIC NOT NULL DEFAULT 0,
    action_type VARCHAR(50),
    amount NUMERIC,
    intraday_price NUMERIC,
    cost_impact NUMERIC,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id UUID PRIMARY KEY,
    run_type VARCHAR(50),
    status VARCHAR(50),
    total_cost NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(100),
    expected TEXT,
    actual TEXT,
    passed BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE day_ahead_schedules
    ADD COLUMN IF NOT EXISTS schedule_date DATE;

ALTER TABLE day_ahead_schedules
    ADD COLUMN IF NOT EXISTS hour INTEGER;

ALTER TABLE day_ahead_schedules
    ADD COLUMN IF NOT EXISTS price NUMERIC;

ALTER TABLE day_ahead_schedules
    ADD COLUMN IF NOT EXISTS demand NUMERIC;

ALTER TABLE day_ahead_schedules
    ADD COLUMN IF NOT EXISTS battery_soc NUMERIC;

ALTER TABLE day_ahead_schedules
    ADD COLUMN IF NOT EXISTS hour_cost NUMERIC;

ALTER TABLE simulation_runs
    ADD COLUMN IF NOT EXISTS total_cost NUMERIC;

ALTER TABLE intraday_actions
    ADD COLUMN IF NOT EXISTS action_date DATE DEFAULT CURRENT_DATE;

ALTER TABLE intraday_actions
    ADD COLUMN IF NOT EXISTS hour INTEGER DEFAULT 0;

ALTER TABLE intraday_actions
    ADD COLUMN IF NOT EXISTS planned_demand NUMERIC;

ALTER TABLE intraday_actions
    ADD COLUMN IF NOT EXISTS actual_demand NUMERIC DEFAULT 0;

ALTER TABLE intraday_actions
    ADD COLUMN IF NOT EXISTS deviation NUMERIC DEFAULT 0;

ALTER TABLE intraday_actions
    ADD COLUMN IF NOT EXISTS intraday_price NUMERIC;

ALTER TABLE intraday_actions
    ADD COLUMN IF NOT EXISTS cost_impact NUMERIC;

ALTER TABLE intraday_actions
    ADD COLUMN IF NOT EXISTS explanation TEXT;

UPDATE intraday_actions
SET action_date = DATE(timestamp)
WHERE action_date IS NULL;

UPDATE intraday_actions
SET hour = EXTRACT(HOUR FROM timestamp)::INTEGER
WHERE hour IS NULL;

UPDATE intraday_actions
SET actual_demand = COALESCE(amount, 0)
WHERE actual_demand IS NULL;

UPDATE intraday_actions
SET deviation = CASE
    WHEN action_type IN ('battery_charge', 'sell_to_market', 'charge_and_sell') THEN -COALESCE(amount, 0)
    ELSE COALESCE(amount, 0)
END
WHERE deviation IS NULL;

ALTER TABLE intraday_actions
    ALTER COLUMN action_date SET NOT NULL;

ALTER TABLE intraday_actions
    ALTER COLUMN hour SET NOT NULL;

ALTER TABLE intraday_actions
    ALTER COLUMN actual_demand SET NOT NULL;

ALTER TABLE intraday_actions
    ALTER COLUMN deviation SET NOT NULL;
