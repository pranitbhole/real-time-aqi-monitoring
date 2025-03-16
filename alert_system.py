import psycopg2
import time
from datetime import datetime

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "air_quality_db",
    "user": "postgres",
    "password": "Inteli54440",
    "host": "localhost",
    "port": "5432"
}

def get_latest_air_quality():
    """Fetch the latest air quality data from the database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT city, aqi, timestamp 
            FROM air_quality 
            ORDER BY timestamp DESC 
            LIMIT 10;
        """)
        records = cursor.fetchall()
        conn.close()
        return records
    except Exception as e:
        print(f"Database error: {e}")
        return []

def determine_alert_level(aqi):
    """Determine the alert level based on AQI value."""
    if aqi <= 2:
        return "Good"
    elif aqi <= 4:
        return "Moderate"
    elif aqi <= 6:
        return "Unhealthy"
    else:
        return "Hazardous"

def store_alert(city, aqi, alert_level):
    """Store alert in the database if it does not already exist."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if a recent alert exists for the same city
        cursor.execute("""
            SELECT COUNT(*) FROM alerts 
            WHERE city = %s AND alert_level = %s 
            AND timestamp >= NOW() - INTERVAL '1 hour'
        """, (city, alert_level))
        
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO alerts (city, aqi, alert_level, timestamp) VALUES (%s, %s, %s, %s)",
                (city, aqi, alert_level, datetime.now())
            )
            conn.commit()
            print(f"🚨 ALERT: {city} - AQI {aqi} - Level: {alert_level}")
        
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

def check_alerts():
    """Check air quality data and trigger alerts."""
    print("🔍 Monitoring air quality in real-time...")
    while True:
        records = get_latest_air_quality()
        for city, aqi, _ in records:
            alert_level = determine_alert_level(aqi)
            store_alert(city, aqi, alert_level)
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    check_alerts()
