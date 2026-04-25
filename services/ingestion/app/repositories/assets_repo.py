from sqlalchemy import text
from sqlalchemy.orm import Session


def save_assets(db: Session, data):
    db.execute(text("""
        INSERT INTO energy_assets (asset_type, capacity, max_charge, max_discharge)
        VALUES (:asset_type, :capacity, :max_charge, :max_discharge)
    """), {
        "asset_type": "battery",
        "capacity": data.battery_capacity,
        "max_charge": data.max_charge,
        "max_discharge": data.max_discharge,
    })

    db.execute(text("""
        INSERT INTO energy_assets (asset_type, max_output)
        VALUES (:asset_type, :max_output)
    """), {
        "asset_type": "gas",
        "max_output": data.gas_max_output,
    })

    db.commit()


def get_assets(db: Session):
    battery = db.execute(text("""
        SELECT capacity, max_charge, max_discharge
        FROM energy_assets
        WHERE asset_type = 'battery'
        ORDER BY id DESC LIMIT 1
    """)).fetchone()

    gas = db.execute(text("""
        SELECT max_output
        FROM energy_assets
        WHERE asset_type = 'gas'
        ORDER BY id DESC LIMIT 1
    """)).fetchone()

    if battery is None and gas is None:
        return None

    return {
        "battery_capacity": float(battery.capacity) if battery and battery.capacity else 0,
        "max_charge": float(battery.max_charge) if battery and battery.max_charge else 0,
        "max_discharge": float(battery.max_discharge) if battery and battery.max_discharge else 0,
        "gas_max_output": float(gas.max_output) if gas and gas.max_output else 0,
        "gas_cost": 0,
    }
