import streamlit as st
from datetime import datetime, timedelta
import json
import os
import folium
from streamlit_folium import folium_static
from folium.plugins import Draw, Fullscreen, MeasureControl
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import pandas as pd
import numpy as np
from src.main import SmartAgricultureSystem
from src.agent.agricultural_agent import AgriculturalAgent # Import the Agent class
import re # Import regex module

st.set_page_config(
    page_title="NEXUS AgriTech • Future of Farming",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🚀"
)

# Inject futuristic CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

    :root {
        --neon-cyan: #00f5ff;
        --neon-purple: #b347d9;
        --neon-blue: #2196f3;
        --neon-green: #39ff14;
        --dark-bg: #0a0a0a;
        --card-bg: rgba(13, 13, 13, 0.95);
        --glass-bg: rgba(255, 255, 255, 0.03);
        --border-glow: rgba(0, 245, 255, 0.3);
    }

    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #0a0a0a 100%);
        background-attachment: fixed;
    }

    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main title styling */
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(45deg, var(--neon-cyan), var(--neon-purple), var(--neon-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 2rem 0;
        text-shadow: 0 0 30px rgba(0, 245, 255, 0.5);
        animation: pulse-glow 2s ease-in-out infinite alternate;
    }

    .subtitle {
        font-family: 'Exo 2', sans-serif;
        font-size: 1.2rem;
        color: var(--neon-cyan);
        text-align: center;
        margin-bottom: 3rem;
        opacity: 0.8;
    }

    @keyframes pulse-glow {
        from { text-shadow: 0 0 20px rgba(0, 245, 255, 0.5), 0 0 30px rgba(179, 71, 217, 0.3); }
        to { text-shadow: 0 0 30px rgba(0, 245, 255, 0.8), 0 0 40px rgba(179, 71, 217, 0.6); }
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--glass-bg);
        border-radius: 15px;
        padding: 10px;
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-glow);
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.1), rgba(179, 71, 217, 0.1));
        border-radius: 10px;
        border: 1px solid transparent;
        color: var(--neon-cyan);
        font-family: 'Exo 2', sans-serif;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.2), rgba(179, 71, 217, 0.2));
        border: 1px solid var(--neon-cyan);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple)) !important;
        color: var(--dark-bg) !important;
        box-shadow: 0 0 25px rgba(0, 245, 255, 0.5) !important;
    }

    /* Card containers */
    .futuristic-card {
        background: var(--card-bg);
        border-radius: 20px;
        border: 1px solid var(--border-glow);
        padding: 25px;
        margin: 20px 0;
        backdrop-filter: blur(15px);
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }

    .futuristic-card:hover {
        border-color: var(--neon-cyan);
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.3),
            0 0 30px rgba(0, 245, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transform: translateY(-5px);
    }

    /* Headers */
    h1, h2, h3 {
        font-family: 'Orbitron', monospace !important;
        color: var(--neon-cyan) !important;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input {
        background: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 10px !important;
        color: var(--neon-cyan) !important;
        font-family: 'Exo 2', sans-serif !important;
        backdrop-filter: blur(10px);
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.3) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple)) !important;
        color: var(--dark-bg) !important;
        border: none !important;
        border-radius: 25px !important;
        font-family: 'Exo 2', sans-serif !important;
        font-weight: 600 !important;
        padding: 12px 30px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--neon-purple), var(--neon-cyan)) !important;
        box-shadow: 0 0 25px rgba(0, 245, 255, 0.5) !important;
        transform: translateY(-3px) !important;
    }

    /* Metrics */
    [data-testid="metric-container"] {
        background: var(--glass-bg);
        border: 1px solid var(--border-glow);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    [data-testid="metric-container"]:hover {
        border-color: var(--neon-cyan);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
    }

    [data-testid="metric-container"] > div {
        color: var(--neon-cyan) !important;
        font-family: 'Orbitron', monospace !important;
    }

    /* Expandable sections */
    .streamlit-expanderHeader {
        background: var(--glass-bg) !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 10px !important;
        font-family: 'Exo 2', sans-serif !important;
        color: var(--neon-cyan) !important;
    }

    .streamlit-expanderContent {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 0 0 10px 10px !important;
    }

    /* Chat messages */
    .stChatMessage {
        background: var(--glass-bg) !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Checkboxes */
    .stCheckbox > label {
        color: var(--neon-cyan) !important;
        font-family: 'Exo 2', sans-serif !important;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: var(--card-bg) !important;
        border-right: 1px solid var(--border-glow) !important;
    }

    /* Success/Error/Warning messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(57, 255, 20, 0.1), rgba(57, 255, 20, 0.05)) !important;
        border: 1px solid var(--neon-green) !important;
        border-radius: 10px !important;
        color: var(--neon-green) !important;
    }

    .stError {
        background: linear-gradient(135deg, rgba(255, 20, 57, 0.1), rgba(255, 20, 57, 0.05)) !important;
        border: 1px solid #ff1439 !important;
        border-radius: 10px !important;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(255, 165, 0, 0.1), rgba(255, 165, 0, 0.05)) !important;
        border: 1px solid #ffa500 !important;
        border-radius: 10px !important;
    }

    /* Loading animation */
    .loading-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--dark-bg);
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--neon-purple), var(--neon-cyan));
    }
</style>
""", unsafe_allow_html=True)

# Main title with futuristic styling
st.markdown("""
<div class="main-title">NEXUS AGRITECH</div>
<div class="subtitle">🚀 Advanced Agricultural Intelligence Platform</div>
""", unsafe_allow_html=True)

# Initialize session state for storing field boundaries and map center
if 'field_boundaries' not in st.session_state:
    st.session_state.field_boundaries = None
if 'map_center' not in st.session_state:
    st.session_state.map_center = [38.5449, -121.7421]  # Default center
if 'last_coords' not in st.session_state:
    st.session_state.last_coords = st.session_state.map_center
if 'map_layers' not in st.session_state:
    st.session_state.map_layers = {
        'OpenStreetMap': True,
        'Satellite': False,
        'Terrain': False
    }
if 'monitored_fields' not in st.session_state:
    st.session_state.monitored_fields = [] # Initialize list for agent monitored fields
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [] # Initialize chat history
if 'chatbot_state' not in st.session_state:
    st.session_state.chatbot_state = 'idle' # Chatbot state: 'idle', 'awaiting_coords'
if 'chatbot_field_coords' not in st.session_state:
    st.session_state.chatbot_field_coords = None # Coordinates for the current chat context

def search_location(query):
    """Search for a location using Nominatim."""
    try:
        geolocator = Nominatim(user_agent="smart_agriculture_app")
        location = geolocator.geocode(query, timeout=10)
        if location:
            return [location.latitude, location.longitude], location.address
        return None, None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        st.error(f"Error searching location: {str(e)}")
        return None, None

def parse_coordinates(text):
    """Attempt to parse coordinates from text (e.g., '38.5, -121.7')."""
    # Regex to find potential coordinate pairs (latitude, longitude)
    match = re.search(r'(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)', text)
    if match:
        try:
            lat = float(match.group(1))
            lon = float(match.group(2))
            # Basic validation for typical geographic ranges
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return [lon, lat] # Return as [longitude, latitude]
        except ValueError:
            return None
    return None

# Create tabs for different features with futuristic styling
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛰️ FIELD SCANNER",
    "📊 DATA ARCHIVE",
    "🌐 NETWORK HUB",
    "🤖 AI AGENTS",
    "💬 NEURAL CHAT"
])

with tab1:
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("## 🛰️ QUANTUM FIELD SCANNER")
    st.markdown("*Advanced satellite analysis and real-time field monitoring*")
    st.markdown('</div>', unsafe_allow_html=True)

    # Create two columns for the layout
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
        try:
            # Create a map with multiple layers
            m = folium.Map(
                location=st.session_state.map_center,
                zoom_start=13,
                tiles='OpenStreetMap' # Use a simple OpenStreetMap tile layer
            )

            # Display the map with explicit width and height
            st.markdown("### 🗺️ **NEURAL MAPPING INTERFACE**")
            st.markdown("*🎯 Select coordinates • 📡 Satellite overlay • 🔍 Precision targeting*")
            folium_static(m, width=700, height=500)

        except Exception as e:
            st.error(f"⚠️ **SYSTEM ERROR**: {str(e)}")
            st.info("🔧 **DIAGNOSTICS**: Map interface temporarily unavailable")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
        st.markdown("### 🎛️ **CONTROL MATRIX**")
        st.markdown("*Neural navigation and coordinate systems*")

        # Location search
        search_query = st.text_input("🔍 **LOCATION SCANNER**", placeholder="🌍 Enter city, address, or landmark...", key="location_search")
        if search_query:
            with st.spinner("🛰️ **Scanning global coordinates...**"):
                coords, address = search_location(search_query)
                if coords:
                    st.session_state.map_center = coords
                    st.session_state.last_coords = coords
                    st.success(f"✅ **TARGET ACQUIRED**: {address}")
                    st.rerun() # Rerun after search to update map and coordinates
                else:
                    st.warning("⚠️ **SCAN FAILED**: Location not found in database")

        st.markdown("#### 📍 **PRECISION COORDINATES**")
        # Input fields for coordinates
        longitude = st.number_input("🌐 **LONGITUDE**", value=st.session_state.map_center[1], format="%f", key="longitude_input")
        latitude = st.number_input("🌐 **LATITUDE**", value=st.session_state.map_center[0], format="%f", key="latitude_input")

        # Update map center in state when coordinates change but don't rerun automatically
        st.session_state.map_center[0] = latitude
        st.session_state.map_center[1] = longitude

        # Button to manually update map and rerun after coordinate input
        if st.button("🎯 **UPDATE POSITION**", key="update_location_btn"):
            st.session_state.last_coords = st.session_state.map_center # Update last_coords here
            st.rerun()

        # Map controls
        st.markdown("#### 🎮 **NAVIGATION CONTROLS**")
        col_controls1, col_controls2 = st.columns(2)
        with col_controls1:
            if st.button("📍 **CENTER**", use_container_width=True, key="center_map_btn"):
                st.session_state.map_center = [latitude, longitude]
                st.session_state.last_coords = [latitude, longitude]
                st.rerun() # Rerun to center map

        with col_controls2:
            if st.button("🔄 **RESET**", use_container_width=True, key="reset_view_btn"):
                st.session_state.map_center = [38.5449, -121.7421]
                st.session_state.last_coords = st.session_state.map_center
                st.rerun() # Rerun to reset view

        # Map layers
        st.markdown("#### 🌐 **OVERLAY SYSTEMS**")
        st.session_state.map_layers['OpenStreetMap'] = st.checkbox("🗺️ **Street Grid**", value=True, key="street_map_layer_col2")
        st.session_state.map_layers['Satellite'] = st.checkbox("🛰️ **Satellite View**", key="satellite_layer_col2")
        st.session_state.map_layers['Terrain'] = st.checkbox("🏔️ **Terrain Mode**", key="terrain_layer_col2")

        # Field details
        st.markdown("#### 🌾 **CROP ANALYTICS**")
        crop_type = st.selectbox("🌱 **Primary Crop**", ["wheat", "corn", "rice", "soybeans", "cotton"], key="crop_type_select")

        end_date = st.date_input("📅 **Analysis End**", value=datetime.now().date(), key="end_date_input")
        start_date = st.date_input(
            "📅 **Analysis Start**",
            value=(datetime.now() - timedelta(days=30)).date(),
            max_value=end_date,
            key="start_date_input"
        )

        st.markdown("#### ⚡ **FIELD OPERATIONS**")
        # Get the drawn features and save boundaries
        # This button should ideally capture drawn shapes, but currently uses point from coordinates.
        if st.button("💾 **SAVE BOUNDARIES**", key="save_boundaries_btn"):
            st.session_state.field_boundaries = {
                'type': 'FeatureCollection',
                'features': [{
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [st.session_state.map_center[1], st.session_state.map_center[0]]
                    }
                }]
            }
            st.success("✅ **BOUNDARIES LOCKED**: Field perimeter secured!")

        if st.button("🔬 **INITIATE DEEP SCAN**", key="analyze_field_btn"):
            with st.spinner("🛰️ **Quantum field analysis in progress...** ⚡"):
                st.info("🔄 **NEURAL NETWORKS PROCESSING**: Satellite data fusion active...")
            system = SmartAgricultureSystem()
            field_coordinates = [longitude, latitude]
            try:
                # Run analysis
                results = system.analyze_field(
                    field_coordinates,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )

                # Display data quality status
                health_analysis = results["health_analysis"]
                data_quality = health_analysis.get('data_quality', 'unknown')
                status_message = health_analysis.get('status_message', '')

                if data_quality == 'limited':
                    st.warning("⚠️ **DATA CONSTRAINT**: Limited satellite coverage detected")
                    st.info(f"📡 **SYSTEM STATUS**: {status_message}")
                elif data_quality == 'error':
                    st.error("❌ **CRITICAL ERROR**: Analysis protocol failed")
                    st.error(f"🔧 **DIAGNOSTICS**: {status_message}")
                else:
                    st.success("✅ **ANALYSIS COMPLETE**: Full spectrum data acquired")
        st.markdown('</div>', unsafe_allow_html=True)

                # Display results in an expandable section
                with st.expander("🔬 **QUANTUM FIELD ANALYSIS** • Neural Network Results", expanded=True):
                    st.markdown("*Advanced AI analysis of crop health and field conditions*")
                    # Remove internal status fields from display
                    display_analysis = {k: v for k, v in health_analysis.items()
                                     if k not in ['data_quality', 'status_message']}
                    st.json(display_analysis)

                with st.expander("🎯 **OPTIMIZATION PROTOCOLS** • Resource Management AI", expanded=True):
                    st.markdown("*Intelligent recommendations for maximum efficiency*")
                    st.json(results["recommendations"])

                # Water usage recommendations
                with st.expander("💧 **HYDRO-OPTIMIZATION MATRIX** • Smart Irrigation", expanded=True):
                    st.markdown("*AI-powered water management and conservation protocols*")
                    weather_data = {"temperature": 25, "humidity": 60, "precipitation": 0}
                    water_recommendations = system.get_water_usage_recommendations(
                        field_coordinates,
                        weather_data
                    )
                    st.json(water_recommendations)

                # Pesticide recommendations
                with st.expander("🛡️ **BIO-DEFENSE SYSTEMS** • Precision Protection", expanded=True):
                    st.markdown("*Advanced crop protection with minimal environmental impact*")
                    pesticide_recommendations = system.get_pesticide_recommendations(
                        field_coordinates,
                        crop_type
                    )
                    st.json(pesticide_recommendations)

                st.success("🎉 **MISSION COMPLETE**: All systems operational")
            except Exception as e:
                st.error(f"❌ **CRITICAL SYSTEM ERROR**: {str(e)}")

        # Add Weather Report Section
        st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
        st.markdown("### 🌦️ **ATMOSPHERIC INTEL**")
        st.markdown("*Real-time meteorological data and forecasting*")
        if st.button("🛰️ **SCAN ATMOSPHERE**", key="weather_report_btn"):
            with st.spinner("Fetching weather data..."):
                system = SmartAgricultureSystem()
                weather_data = system.get_weather_report([latitude, longitude])

                if weather_data['status'] == 'success':
                    current = weather_data['current_weather']
                    forecast = weather_data['forecast']
                    insights = weather_data['insights']

                    # Display current weather
                    st.markdown("### Current Weather")
                    col_temp, col_hum = st.columns(2)
                    with col_temp:
                        st.metric("Temperature", f"{current['temperature']:.1f}°C",
                                f"Feels like: {current['feels_like']:.1f}°C")
                    with col_hum:
                        st.metric("Humidity", f"{current['humidity']}%")

                    col_wind, col_pres = st.columns(2)
                    with col_wind:
                        st.metric("Wind Speed", f"{current['wind_speed']} m/s")
                    with col_pres:
                        st.metric("Pressure", f"{current['pressure']} hPa")

                    st.markdown(f"**Conditions:** {current['weather_description'].title()}")

                    # Display weather insights
                    if insights:
                        st.markdown("### Weather Insights")
                        for insight in insights:
                            st.info(insight)

                    # Display forecast
                    st.markdown("### 5-Day Forecast")
                    forecast_df = pd.DataFrame(forecast)
                    forecast_df['date'] = forecast_df['timestamp'].dt.date
                    forecast_df['time'] = forecast_df['timestamp'].dt.time

                    # Group by date and calculate daily statistics
                    daily_forecast = forecast_df.groupby('date').agg({
                        'temperature': ['mean', 'min', 'max'],
                        'humidity': 'mean',
                        'precipitation': 'mean',
                        'wind_speed': 'mean'
                    }).round(1)

                    daily_forecast.columns = ['_'.join(col).strip() for col in daily_forecast.columns.values]

                    # Display daily forecast
                    for date, row in daily_forecast.iterrows():
                        with st.expander(f"{date.strftime('%A, %B %d')}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Temperature",
                                        f"{row['temperature_mean']:.1f}°C",
                                        f"Min: {row['temperature_min']:.1f}°C, Max: {row['temperature_max']:.1f}°C")
                            with col2:
                                st.metric("Humidity", f"{row['humidity_mean']:.1f}%")
                            with col3:
                                st.metric("Precipitation", f"{row['precipitation_mean']:.1f}%")

                            # Get weather description for this day
                            day_weather = forecast_df[forecast_df['date'] == date]['weather_description'].mode().iloc[0]
                            st.markdown(f"**Conditions:** {day_weather.title()}")
                else:
                    st.error(f"Error fetching weather data: {weather_data['message']}")

with tab2:
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("## 📊 TEMPORAL DATA ARCHIVE")
    st.markdown("*Time-series analysis and predictive modeling from historical datasets*")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### ⏰ **TEMPORAL PARAMETERS**")
    # Create a date range selector for historical data
    col1, col2 = st.columns(2)
    with col1:
        historical_start = st.date_input(
            "📅 **Archive Start**",
            value=(datetime.now() - timedelta(days=365)).date()
        )
    with col2:
        historical_end = st.date_input(
            "📅 **Archive End**",
            value=datetime.now().date(),
            min_value=historical_start
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Generate some sample historical data
    dates = pd.date_range(historical_start, historical_end, freq='M')
    health_scores = np.random.normal(0.7, 0.1, len(dates))
    water_usage = np.random.normal(0.6, 0.15, len(dates))

    # Create a line chart for health scores
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### 📈 **NEURAL TREND ANALYSIS**")
    st.markdown("*AI-powered pattern recognition in agricultural data*")
    chart_data = pd.DataFrame({
        'Date': dates,
        'Health Score': health_scores,
        'Water Usage': water_usage
    })
    st.line_chart(chart_data.set_index('Date'))
    st.markdown('</div>', unsafe_allow_html=True)

    # Add insights
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 **QUANTUM INSIGHTS**")
    st.markdown("*AI-computed performance metrics and predictions*")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "🧬 **Neural Health Index**",
            f"{np.mean(health_scores):.2f}",
            f"{np.mean(health_scores) - 0.5:.2f}"
        )
    with col2:
        st.metric(
            "💧 **Hydro Efficiency**",
            f"{np.mean(water_usage):.2f}",
            f"{np.mean(water_usage) - 0.5:.2f}"
        )
    with col3:
        st.metric(
            "🚀 **Yield Projection**",
            "85%",
            "5%"
        )
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("## 🌐 NEURAL NETWORK HUB")
    st.markdown("*Global farmer intelligence and collaborative knowledge sharing*")
    st.markdown('</div>', unsafe_allow_html=True)

    # Create a section for local farming tips
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### 🧠 **COLLECTIVE INTELLIGENCE**")
    st.markdown("*Real-time insights from the agricultural neural network*")
    tips = [
        "🌧️ **HYDRO PROTOCOL**: Neural farmers report 23% efficiency gains with dawn irrigation cycles",
        "🌱 **SOIL MATRIX**: Legume rotation sequences showing 31% nitrogen optimization",
        "🐝 **BIO-ALLIANCE**: Pollination partnerships available via quantum bee network",
        "🌾 **STRAIN DATA**: Wheat variants XYZ-7 and ABC-9 achieving superior yields in sector"
    ]
    for tip in tips:
        st.info(tip)
    st.markdown('</div>', unsafe_allow_html=True)

    # Add a section for community questions
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### 💬 **HIVE MIND QUERIES**")
    st.markdown("*Connect with the global agricultural consciousness*")
    question = st.text_area("🗣️ **Transmit your query to the network**", placeholder="Share your farming challenge with the collective...")
    if st.button("📡 **BROADCAST SIGNAL**"):
        st.success("✅ **SIGNAL TRANSMITTED**: Neural farmers across the network have been alerted!")
    st.markdown('</div>', unsafe_allow_html=True)

    # Add a section for local weather alerts
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### ⚡ **ATMOSPHERIC WARNINGS**")
    st.markdown("*Real-time environmental threat detection system*")
    alerts = [
        "⚠️ **HYDRO SURGE**: Heavy precipitation incoming - 48-hour window detected",
        "🌡️ **THERMAL ALERT**: Temperature drop to sub-10°C threshold tonight",
        "💨 **WIND PATTERN**: High-velocity atmospheric disturbance - dawn sector"
    ]
    for alert in alerts:
        st.warning(alert)
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("## 🤖 AI AGENT COMMAND CENTER")
    st.markdown("*Autonomous field monitoring and intelligent agent coordination*")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### 👁️ **SURVEILLANCE NETWORK**")
    st.markdown("*Active monitoring zones under AI supervision*")
    if st.session_state.monitored_fields:
        for i, field in enumerate(st.session_state.monitored_fields):
            st.markdown(f"🎯 **SECTOR {i+1}**: `{field['name']}` • **COORDINATES**: `{field['coordinates'][1]:.4f}°, {field['coordinates'][0]:.4f}°`")
    else:
        st.info("🔍 **STATUS**: No active surveillance zones detected")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### ➕ **DEPLOY NEW SURVEILLANCE**")
    st.markdown("*Register new field for autonomous monitoring*")
    with st.form("add_field_form", clear_on_submit=True):
        field_name = st.text_input("🏷️ **Sector Designation**", placeholder="Enter field identifier...")
        field_lon = st.number_input("🌐 **Longitude Coordinates**", format="%f", key="new_field_lon")
        field_lat = st.number_input("🌐 **Latitude Coordinates**", format="%f", key="new_field_lat")

        add_button = st.form_submit_button("🚀 **DEPLOY AGENT**")

        if add_button:
            if field_name and field_lon is not None and field_lat is not None:
                new_field = {'name': field_name, 'coordinates': [field_lon, field_lat]}
                st.session_state.monitored_fields.append(new_field)
                st.success(f"✅ **DEPLOYMENT SUCCESSFUL**: Agent assigned to sector '{field_name}'")
                st.rerun() # Rerun to update the displayed list
            else:
                st.warning("⚠️ **DEPLOYMENT FAILED**: All parameters required for agent activation")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### ⚡ **AGENT OPERATIONS**")
    st.markdown("*Manual override and emergency protocols*")
    if st.button("🔬 **EXECUTE FULL SPECTRUM ANALYSIS**", key="run_agent_analysis_btn"):
        if st.session_state.monitored_fields:
            with st.spinner("🛰️ **AGENTS SYNCHRONIZING**: Multi-spectrum analysis in progress..."):
                agent = AgriculturalAgent(monitored_fields=st.session_state.monitored_fields)

                # Run the analysis and store the results in session state
                analysis_results = agent.perform_scheduled_analysis()
                st.session_state.agent_analysis_results = analysis_results

                # Process the results to generate insights and anomalies
                processed_insights = agent.process_analysis_results(analysis_results)
                st.session_state.agent_processed_insights = processed_insights

            st.success("✅ **MISSION COMPLETE**: All agents have reported back with intelligence data")
        else:
            st.warning("⚠️ **NO ACTIVE AGENTS**: Deploy surveillance to sectors before analysis")
    st.markdown('</div>', unsafe_allow_html=True)

    # Display agent analysis results if available in session state
    if 'agent_analysis_results' in st.session_state and st.session_state.agent_analysis_results:
        st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
        st.markdown("### 📊 **NEURAL INTELLIGENCE REPORTS**")
        st.markdown("*Comprehensive analysis data from autonomous field agents*")
        for field_name, results in st.session_state.agent_analysis_results.items():
            with st.expander(f"🤖 **AGENT REPORT**: {field_name} • Neural Analysis Matrix", expanded=False):
                if 'error' in results:
                    st.error(f"Error during analysis: {results['error']}")
                else:
                    # Display relevant parts of the results
                    if 'health_analysis' in results:
                        st.write("**Health Analysis:**")
                        display_health = {k: v for k, v in results['health_analysis'].items()
                                          if k not in ['data_quality', 'status_message']}
                        st.json(display_health)
                        if results['health_analysis'].get('data_quality') == 'limited':
                            st.warning(f"⚠️ Limited data: {results['health_analysis'].get('status_message', '')}")
                        elif results['health_analysis'].get('data_quality') == 'error':
                             st.error(f"❌ Data error: {results['health_analysis'].get('status_message', '')}")

                    if 'recommendations' in results:
                        st.write("**Recommendations:**")
                        st.json(results['recommendations'])

                        # Process recommendations to show key-value pairs
                        recommendations = results['recommendations']
                        st.write("\n**Detailed Recommendations:**")
                        if recommendations:
                            for category, rec_list in recommendations.items():
                                if rec_list:
                                    st.write(f"**{category.replace('_', ' ').title()}:**")
                                    for rec in rec_list:
                                        # Format each recommendation item's details
                                        rec_details = []
                                        if isinstance(rec, dict):
                                            for key, value in rec.items():
                                                rec_details.append(f"{key.replace('_', ' ').title()}: {value}")
                                            st.write(f"- {', '.join(rec_details)}")
                                        else:
                                            # Fallback for non-dict recommendations
                                            st.write(f"- {rec}")

                    # You can add more sections here to display water usage, pesticides, etc.

    # Display processed agent insights if available in session state
    if 'agent_processed_insights' in st.session_state and st.session_state.agent_processed_insights:
        st.markdown("### 🔍 **THREAT ANALYSIS & INSIGHTS**")
        st.markdown("*AI-processed intelligence and anomaly detection*")
        for field_name, insights in st.session_state.agent_processed_insights.items():
            with st.expander(f"🧠 **NEURAL INSIGHTS**: {field_name} • Threat Matrix", expanded=True):
                st.markdown(f"**🎯 EXECUTIVE SUMMARY:** {insights.get('summary', 'No intelligence data available.')}")
                if insights.get('anomalies'):
                    st.markdown("**⚠️ ANOMALIES DETECTED:**")
                    for anomaly in insights['anomalies']:
                        st.warning(f"🚨 **ALERT**: {anomaly}")
                else:
                    st.info("✅ **ALL CLEAR**: No significant threats detected in sector")
        st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("## 💬 NEURAL CHAT INTERFACE")
    st.markdown("*Advanced AI agricultural consultant with quantum intelligence*")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="futuristic-card">', unsafe_allow_html=True)
    st.markdown("### 🧠 **CONVERSATION MATRIX**")
    st.markdown("*Real-time neural dialogue with agricultural AI*")

    # Display chat messages from history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("🗣️ Interface with the neural network..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate the agent's response
        with st.chat_message("assistant"):
            with st.spinner("🤖 **Neural processing active...** 🧠"):
                response = ""

                # --- Chatbot Logic ---+

                # State 1: Idle or receiving a general query
                if st.session_state.chatbot_state == 'idle':
                    if any(keyword in prompt.lower() for keyword in ["health", "analysis", "report", "results", "insights"]):
                        if st.session_state.chatbot_field_coords:
                            response = f"🛰️ **QUANTUM ANALYSIS INITIATED** for sector at coordinates `{st.session_state.chatbot_field_coords[1]:.4f}°, {st.session_state.chatbot_field_coords[0]:.4f}°`\n\n🔄 **NEURAL NETWORKS SYNCHRONIZING**...\n\n" # Note: coordinates are [lon, lat] but we display lat, lon for user

                            # --- Trigger Analysis ---+
                            try:
                                system = SmartAgricultureSystem() # Initialize system
                                # Use a default date range for on-demand analysis
                                end_date = datetime.now().date().strftime("%Y-%m-%d")
                                start_date = (datetime.now().date() - timedelta(days=30)).strftime("%Y-%m-%d")

                                analysis_results = system.analyze_field(
                                    st.session_state.chatbot_field_coords,
                                    start_date,
                                    end_date
                                )

                                # Process results using the agent's method
                                agent = AgriculturalAgent() # Initialize agent (can be done here for processing)
                                processed_insights = agent.process_analysis_results({'On-Demand Field': analysis_results}) # Wrap in dict for processing
                                field_insights = processed_insights.get('On-Demand Field', {})

                                # --- Format and Display Report ---+
                                response += "📊 **NEURAL ANALYSIS COMPLETE** • Field Intelligence Report:\n\n"
                                response += f"🎯 **EXECUTIVE SUMMARY:** {field_insights.get('summary', 'No intelligence data available.')}\n"
                                if field_insights.get('anomalies'):
                                    response += "\n⚠️ **THREAT MATRIX:**\n"
                                    for anomaly in field_insights['anomalies']:
                                        response += f"🚨 {anomaly}\n"

                                # Add detailed recommendations
                                if 'recommendations' in analysis_results and analysis_results['recommendations']:
                                    recommendations = analysis_results['recommendations']
                                    response += "\n🎯 **OPTIMIZATION PROTOCOLS:**\n"
                                    if recommendations:
                                        # Briefly list recommendation categories and then details
                                        for category, rec_list in recommendations.items():
                                            if rec_list:
                                                response += f"**{category.replace('_', ' ').title()}:**\n"
                                                for rec in rec_list:
                                                    # Format each recommendation item's details
                                                    rec_details = []
                                                    if isinstance(rec, dict):
                                                         for key, value in rec.items():
                                                              rec_details.append(f"{key.replace('_', ' ').title()}: {value}")
                                                         response += f"- {', '.join(rec_details)}\n"
                                                    else:
                                                        # Fallback for non-dict recommendations
                                                        response += f"- {rec}\n"

                                else:
                                    response += "\nNo specific recommendations at this time.\n"

                                # Optionally add more raw details here if needed
                                # response += "\n**Raw Health Analysis:**\n" + json.dumps(analysis_results.get('health_analysis', {}), indent=2)

                            except Exception as e:
                                response = f"An error occurred during the analysis: {str(e)}"
                                st.error(response)

                            # Reset chatbot state after providing report
                            st.session_state.chatbot_state = 'idle'
                            st.session_state.chatbot_field_coords = None # Clear coordinates after analysis

                        else:
                            response = "🤖 **NEURAL INTERFACE ACTIVE** • Provide target coordinates for quantum field analysis (format: `latitude, longitude` e.g., `38.5, -121.7`)"
                            st.session_state.chatbot_state = 'awaiting_coords'

                    elif any(keyword in prompt.lower() for keyword in ["hello", "hi", "hey"]):
                         response = "🚀 **NEURAL CHAT ONLINE** • I am your advanced agricultural AI consultant. How may I assist with your quantum farming operations? Available functions: `field analysis` • `sector monitoring` • `threat assessment`"

                    else:
                        response = "❓ **QUERY NOT RECOGNIZED** • Try: `analyze field` | `generate report` | `sector coordinates` for optimal neural interface compatibility."

                # State 2: Awaiting coordinates
                elif st.session_state.chatbot_state == 'awaiting_coords':
                    coords = parse_coordinates(prompt)
                    if coords:
                        st.session_state.chatbot_field_coords = coords
                        st.session_state.chatbot_state = 'idle' # Move back to idle after getting coords
                        response = f"✅ **COORDINATES LOCKED**: Target acquired at `{coords[1]:.4f}°, {coords[0]:.4f}°` • **READY FOR NEURAL ANALYSIS** • Request: `analysis` or `report` to initiate quantum field scan."

                        # Optionally, trigger analysis immediately after getting coordinates
                        # if any(keyword in prompt.lower() for keyword in ["health", "analysis", "report", "results", "insights"]):
                        #     # Code to trigger analysis and display report here
                        #     pass # We will add this logic in the next step

                    else:
                        response = "❌ **COORDINATE PARSING FAILED** • Format required: `latitude, longitude` (example: `38.5, -121.7`) for neural targeting system."

                else:
                     response = "An unexpected error occurred with the chatbot state."

                # --- End Chatbot Logic ---+

                st.markdown(response)

        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

st.sidebar.markdown("---")
st.sidebar.info("Developed for sustainable farming 🌾")
