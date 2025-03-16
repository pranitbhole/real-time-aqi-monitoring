import requests
import psycopg2
import time
from datetime import datetime

# OpenWeather API details
API_KEY = "d83733ad675dc22d271bf1242bdfc5a6"
BASE_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

# List of 25 cities (10 from India, 15 global)
CITIES = {
    "Delhi": (28.6139, 77.2090), "Mumbai": (19.0760, 72.8777), "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707), "Hyderabad": (17.3850, 78.4867), "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567), "Ahmedabad": (23.0225, 72.5714), "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "New York": (40.7128, -74.0060), "London": (51.5074, -0.1278), "Tokyo": (35.6895, 139.6917),
    "Beijing": (39.9042, 116.4074), "Paris": (48.8566, 2.3522), "Moscow": (55.7558, 37.6173),
    "Sydney": (-33.8688, 151.2093), "Los Angeles": (34.0522, -118.2437), "Berlin": (52.5200, 13.4050),
    "Toronto": (43.651070, -79.347015), "Dubai": (25.276987, 55.296249), "Singapore": (1.3521, 103.8198),
    "Seoul": (37.5665, 126.9780), "Istanbul": (41.0082, 28.9784), "São Paulo": (-23.5505, -46.6333)
}

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "air_quality_db",
    "user": "postgres",
    "password": "Inteli54440",
    "host": "localhost",
    "port": "5432"
}

def fetch_air_quality(lat, lon):
    url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def save_to_db(city, data):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        aqi = data['list'][0]['main']['aqi']
        components = data['list'][0]['components']
        timestamp = datetime.utcnow()
        
        cursor.execute(
            """
            INSERT INTO air_quality (city, aqi, pm10, pm2_5, no2, so2, co, o3, nh3, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (city, aqi, components['pm10'], components['pm2_5'], components['no2'],
             components['so2'], components['co'], components['o3'], components['nh3'], timestamp)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Data inserted for {city}")
    except Exception as e:
        print(f"Database error: {e}")

def main():
    while True:
        for city, (lat, lon) in CITIES.items():
            print(f"Fetching data for {city}...")
            data = fetch_air_quality(lat, lon)
            if data:
                save_to_db(city, data)
        print("Waiting 10 minutes before next fetch...")
        time.sleep(600)  # Wait 10 minutes before next fetch

if __name__ == "__main__":
    main()
