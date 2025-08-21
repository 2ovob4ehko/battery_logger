#!/usr/bin/env python3
import subprocess

import psutil
import csv
from datetime import datetime, timedelta
from pathlib import Path
from gi.repository import GLib

# Шлях до логів
log_dir = Path(GLib.get_user_data_dir()) / "com.mmaaxx.BatteryLogger"
log_dir.mkdir(parents=True, exist_ok=True)

minute_log = log_dir / "battery_log.csv"

def get_power_profile():
    try:
        result = subprocess.run(['powerprofilesctl', 'get'], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

# Зчитування наявних записів
def read_csv(path):
    if not path.exists():
        return []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

# Запис у CSV
def append_csv(path, fieldnames, row):
    exists = path.exists()
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(row)

# Видалення застарілих рядків
def trim_old_data(path, max_age_minutes):
    rows = read_csv(path)
    cutoff = datetime.now() - timedelta(minutes=max_age_minutes)
    filtered = [r for r in rows if datetime.fromisoformat(r["timestamp"]) >= cutoff]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else ["timestamp", "percent", "charging"])
        writer.writeheader()
        writer.writerows(filtered)

def log_battery():
    battery = psutil.sensors_battery()
    if battery is None:
        print("Battery data not available.")
        return

    now = datetime.now().replace(second=0, microsecond=0)
    charging = int(battery.power_plugged)
    if get_power_profile() == 'power-saver' and charging == 0:
        charging = 2
    row = {
        "timestamp": now.isoformat(),
        "percent": round(battery.percent, 2),
        "charging": charging
    }

    append_csv(minute_log, ["timestamp", "percent", "charging"], row)
    trim_old_data(minute_log, 24 * 60 * 14)  # 14 днів

if __name__ == "__main__":
    log_battery()
