import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Database Connection
DB_CONFIG = {
    "dbname": "air_quality_db",
    "user": "postgres",
    "password": "Inteli54440",
    "host": "localhost",
    "port": "5432",
}
engine = create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")

def fetch_air_quality_data():
    """Fetch air quality data from the database."""
    query = """
    SELECT city, aqi, pm10, pm2_5, no2, so2, co, o3, nh3, timestamp
    FROM air_quality
    ORDER BY timestamp DESC;
    """
    df = pd.read_sql(query, engine)
    return df

def categorize_aqi(aqi):
    """Categorize AQI levels for OpenWeather's scale (1-5)."""
    if aqi == 1:
        return "Good"
    elif aqi == 2:
        return "Fair"
    elif aqi == 3:
        return "Moderate"
    elif aqi == 4:
        return "Poor"
    elif aqi == 5:
        return "Very Poor"
    else:
        return "Hazardous"

# Streamlit UI
st.set_page_config(page_title="AQI Alert System", layout="wide")
st.title("🌍 AQI Alert System")

# Fetch data
df = fetch_air_quality_data()
df = df.dropna(subset=['aqi'])  # Drop rows with missing AQI values
df["AQI Category"] = df["aqi"].apply(categorize_aqi)

# Predefined Latitude and Longitude for Cities
city_coordinates = {
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Beijing": {"lat": 39.9042, "lon": 116.4074},
    "Bangkok": {"lat": 13.7563, "lon": 100.5018},
    "Jakarta": {"lat": -6.2088, "lon": 106.8456},
    "Seoul": {"lat": 37.5665, "lon": 126.9780},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Karachi": {"lat": 24.8607, "lon": 67.0011},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Dhaka": {"lat": 23.8103, "lon": 90.4125},
}

df["lat"] = df["city"].map(lambda city: city_coordinates.get(city, {}).get("lat", None))
df["lon"] = df["city"].map(lambda city: city_coordinates.get(city, {}).get("lon", None))
df = df.dropna(subset=["lat", "lon"])  # Remove rows without coordinates

# Top 5 Cities with Worst AQI (Unique Cities)
st.subheader("🚨 Top 5 Cities with Worst AQI")
top_cities = df.sort_values(by="aqi", ascending=False).drop_duplicates(subset=["city"]).head(5)

col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

for i, row in enumerate(top_cities.itertuples()):
    with columns[i]:
        st.markdown(
            f"""
            <div style="background-color:#FF4B4B; padding:10px; border-radius:10px; text-align:center;">
                <h4 style="color:white;">🏙️ {row.city}</h4>
                <h3 style="color:white;">AQI: {row.aqi}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

# Layout for Heatmap and World AQI Map
st.subheader("🌡️ Heatmap & World AQI Map")
col1, col2 = st.columns(2)

with col1:
    heatmap_fig = px.density_heatmap(df, x="city", y="aqi", z="aqi", color_continuous_scale="reds", title="Heatmap of AQI Levels by City")
    heatmap_fig.update_layout(height=350)
    st.plotly_chart(heatmap_fig, use_container_width=True)

with col2:
    map_fig = px.scatter_geo(df, lat="lat", lon="lon", size="aqi",
                             color="aqi", hover_name="city", projection="natural earth",
                             title="AQI Levels Across the World", color_continuous_scale="reds")
    st.plotly_chart(map_fig, use_container_width=True)

# Line Chart for AQI Over Time
st.subheader("📈 AQI Trend Over Time")
selected_city = st.selectbox("Select a city to view AQI trends:", df["city"].unique())
filtered_df = df[df["city"] == selected_city]
line_fig = px.line(filtered_df, x="timestamp", y="aqi", title=f"AQI Trend for {selected_city}")
st.plotly_chart(line_fig, use_container_width=True)

# Real-time AQI Alerts
st.subheader("🚨 Real-time AQI Alerts")

# Filter for critical AQI levels (Very Poor or Hazardous)
critical_aqi_df = df[df["aqi"] >= 5]  # Adjust threshold as needed

# Keep only the latest critical AQI alert per city
critical_aqi_df = critical_aqi_df.sort_values(by="timestamp", ascending=False).drop_duplicates(subset=["city"])

if not critical_aqi_df.empty:
    for row in critical_aqi_df.itertuples():
        color = "#FF4B4B" if row.aqi >= 4 else "#FFA500"  # Red for Hazardous, Orange for Very Poor
        st.markdown(
            f"""
            <div style="background-color:{color}; padding:10px; border-radius:10px; text-align:center;">
                <h4 style="color:white;">🚨 {row.city}</h4>
                <h3 style="color:white;">AQI: {row.aqi}</h3>
                <p style="color:white;">Timestamp: {row.timestamp}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.success("No critical AQI alerts at the moment. ✅")

st.success("Dashboard updated in real-time! ✅")
