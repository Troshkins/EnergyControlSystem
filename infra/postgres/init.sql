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
    run_id UUID,
    timestamp TIMESTAMP NOT NULL,
    grid_usage NUMERIC,
    gas_usage NUMERIC,
    battery_charge NUMERIC,
    battery_discharge NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intraday_actions (
    id SERIAL PRIMARY KEY,
    run_id UUID,
    timestamp TIMESTAMP NOT NULL,
    action_type VARCHAR(50),
    amount NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id UUID PRIMARY KEY,
    run_type VARCHAR(50),
    status VARCHAR(50),
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
