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

st.set_page_config(page_title="Smart Agriculture System", layout="wide")
st.title("🌱 Smart Agriculture System for Farmers")

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

# Create tabs for different features
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Field Analysis", "Historical Data", "Community Insights", "Agent Management", "Chatbot"])

with tab1:
    st.header("Field Analysis")
    
    # Create two columns for the layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        try:
            # Create a map with multiple layers
            m = folium.Map(
                location=st.session_state.map_center,
                zoom_start=13,
                tiles='OpenStreetMap' # Use a simple OpenStreetMap tile layer
            )
            
            # Display the map with explicit width and height
            st.subheader("Field Location")
            st.write("Search for a location, click on the map, or use the input fields to set coordinates")
            folium_static(m, width=700, height=500)
            
        except Exception as e:
            st.error(f"Error creating map: {str(e)}")
            st.info("Could not display map.")

    with col2:
        st.subheader("Field Details")
        
        # Location search
        search_query = st.text_input("Search Location", placeholder="Enter city, address, or landmark", key="location_search")
        if search_query:
            coords, address = search_location(search_query)
            if coords:
                st.session_state.map_center = coords
                st.session_state.last_coords = coords
                st.success(f"Found: {address}")
                st.rerun() # Rerun after search to update map and coordinates
            else:
                st.warning("Location not found. Please try a different search term.")
        
        # Input fields for coordinates
        longitude = st.number_input("Longitude", value=st.session_state.map_center[1], format="%f", key="longitude_input")
        latitude = st.number_input("Latitude", value=st.session_state.map_center[0], format="%f", key="latitude_input")
        
        # Update map center in state when coordinates change but don't rerun automatically
        st.session_state.map_center[0] = latitude
        st.session_state.map_center[1] = longitude

        # Button to manually update map and rerun after coordinate input
        if st.button("Update Location", key="update_location_btn"):
            st.session_state.last_coords = st.session_state.map_center # Update last_coords here
            st.rerun()

        # Map controls
        st.subheader("Map Controls")
        col_controls1, col_controls2 = st.columns(2)
        with col_controls1:
            if st.button("Center Map", use_container_width=True, key="center_map_btn"):
                st.session_state.map_center = [latitude, longitude]
                st.session_state.last_coords = [latitude, longitude]
                st.rerun() # Rerun to center map
        
        with col_controls2:
            if st.button("Reset View", use_container_width=True, key="reset_view_btn"):
                st.session_state.map_center = [38.5449, -121.7421]
                st.session_state.last_coords = st.session_state.map_center
                st.rerun() # Rerun to reset view
        
        # Map layers
        st.subheader("Map Layers")
        st.session_state.map_layers['OpenStreetMap'] = st.checkbox("Street Map", value=True, key="street_map_layer_col2")
        st.session_state.map_layers['Satellite'] = st.checkbox("Satellite View", key="satellite_layer_col2")
        st.session_state.map_layers['Terrain'] = st.checkbox("Terrain View", key="terrain_layer_col2")

        # Note: The checkbox state needs to be handled to update the map layers. This will require rebuilding the map based on the checked layers.
        # For now, the map display in col1 is simplified, but we'll address dynamic layers later.
        
        # Field details
        st.subheader("Field Information")
        crop_type = st.selectbox("Crop Type", ["wheat", "corn", "rice", "soybeans", "cotton"], key="crop_type_select")
        
        end_date = st.date_input("End Date", value=datetime.now().date(), key="end_date_input")
        start_date = st.date_input(
            "Start Date", 
            value=(datetime.now() - timedelta(days=30)).date(),
            max_value=end_date,
            key="start_date_input"
        )
        
        # Get the drawn features and save boundaries
        # This button should ideally capture drawn shapes, but currently uses point from coordinates.
        if st.button("Save Field Boundaries", key="save_boundaries_btn"):
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
            st.success("Field boundaries saved!")

        if st.button("Analyze Field", key="analyze_field_btn"):
            st.info("Running analysis. Please wait...")
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
                    st.warning("⚠️ Limited satellite data available")
                    st.info(status_message)
                elif data_quality == 'error':
                    st.error("❌ Error in analysis")
                    st.error(status_message)
                else:
                    st.success("✅ Analysis completed successfully")
                
                # Display results in an expandable section
                with st.expander("Field Analysis Results", expanded=True):
                    # Remove internal status fields from display
                    display_analysis = {k: v for k, v in health_analysis.items() 
                                     if k not in ['data_quality', 'status_message']}
                    st.json(display_analysis)
                
                with st.expander("Resource Optimization Recommendations", expanded=True):
                    st.json(results["recommendations"])
                
                # Water usage recommendations
                with st.expander("Water Usage Recommendations", expanded=True):
                    weather_data = {"temperature": 25, "humidity": 60, "precipitation": 0}
                    water_recommendations = system.get_water_usage_recommendations(
                        field_coordinates, 
                        weather_data
                    )
                    st.json(water_recommendations)
                
                # Pesticide recommendations
                with st.expander("Pesticide Usage Recommendations", expanded=True):
                    pesticide_recommendations = system.get_pesticide_recommendations(
                        field_coordinates,
                        crop_type
                    )
                    st.json(pesticide_recommendations)
                
                st.success("Analysis complete!")
            except Exception as e:
                st.error(f"Error running analysis: {str(e)}")

        # Add Weather Report Section
        st.subheader("Weather Report")
        if st.button("Get Weather Report", key="weather_report_btn"):
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
    st.header("Historical Data Analysis")
    
    # Create a date range selector for historical data
    col1, col2 = st.columns(2)
    with col1:
        historical_start = st.date_input(
            "Historical Start Date",
            value=(datetime.now() - timedelta(days=365)).date()
        )
    with col2:
        historical_end = st.date_input(
            "Historical End Date",
            value=datetime.now().date(),
            min_value=historical_start
        )
    
    # Generate some sample historical data
    dates = pd.date_range(historical_start, historical_end, freq='M')
    health_scores = np.random.normal(0.7, 0.1, len(dates))
    water_usage = np.random.normal(0.6, 0.15, len(dates))
    
    # Create a line chart for health scores
    st.subheader("Field Health Trends")
    chart_data = pd.DataFrame({
        'Date': dates,
        'Health Score': health_scores,
        'Water Usage': water_usage
    })
    st.line_chart(chart_data.set_index('Date'))
    
    # Add insights
    st.subheader("Key Insights")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Average Health Score",
            f"{np.mean(health_scores):.2f}",
            f"{np.mean(health_scores) - 0.5:.2f}"
        )
    with col2:
        st.metric(
            "Water Usage Efficiency",
            f"{np.mean(water_usage):.2f}",
            f"{np.mean(water_usage) - 0.5:.2f}"
        )
    with col3:
        st.metric(
            "Yield Prediction",
            "85%",
            "5%"
        )

with tab3:
    st.header("Community Insights")
    
    # Create a section for local farming tips
    st.subheader("Local Farming Tips")
    tips = [
        "🌧️ Local farmers report good results with early morning irrigation",
        "🌱 Consider crop rotation with legumes to improve soil health",
        "🐝 Local beekeepers are available for pollination services",
        "🌾 Wheat varieties XYZ and ABC are performing well in this region"
    ]
    for tip in tips:
        st.info(tip)
    
    # Add a section for community questions
    st.subheader("Ask the Community")
    question = st.text_area("Post your question to the farming community")
    if st.button("Submit Question"):
        st.success("Question submitted! Local farmers will be notified.")
    
    # Add a section for local weather alerts
    st.subheader("Local Weather Alerts")
    alerts = [
        "⚠️ Heavy rainfall expected in the next 48 hours",
        "🌡️ Temperature expected to drop below 10°C tonight",
        "💨 Strong winds forecasted for tomorrow morning"
    ]
    for alert in alerts:
        st.warning(alert)

with tab4:
    st.header("Agent Management")
    
    st.subheader("Monitored Fields")
    if st.session_state.monitored_fields:
        for i, field in enumerate(st.session_state.monitored_fields):
            st.write(f"{i+1}. {field['name']} ({field['coordinates'][1]:.4f}, {field['coordinates'][0]:.4f})")
    else:
        st.info("No fields are currently being monitored by the agent.")

    st.subheader("Add New Field to Monitor")
    with st.form("add_field_form", clear_on_submit=True):
        field_name = st.text_input("Field Name")
        field_lon = st.number_input("Longitude", format="%f", key="new_field_lon")
        field_lat = st.number_input("Latitude", format="%f", key="new_field_lat")
        
        add_button = st.form_submit_button("Add Field")
        
        if add_button:
            if field_name and field_lon is not None and field_lat is not None:
                new_field = {'name': field_name, 'coordinates': [field_lon, field_lat]}
                st.session_state.monitored_fields.append(new_field)
                st.success(f"Added field '{field_name}' to the monitoring list.")
                st.rerun() # Rerun to update the displayed list
            else:
                st.warning("Please fill in all fields to add a new field.")

    st.subheader("Manual Agent Actions")
    if st.button("Run Scheduled Analysis Now", key="run_agent_analysis_btn"):
        if st.session_state.monitored_fields:
            agent = AgriculturalAgent(monitored_fields=st.session_state.monitored_fields)
            
            # Run the analysis and store the results in session state
            analysis_results = agent.perform_scheduled_analysis()
            st.session_state.agent_analysis_results = analysis_results

            # Process the results to generate insights and anomalies
            processed_insights = agent.process_analysis_results(analysis_results)
            st.session_state.agent_processed_insights = processed_insights

            st.success("Scheduled analysis initiated for monitored fields. Results displayed below.")
        else:
            st.warning("Add fields to monitor before running analysis.")

    # Display agent analysis results if available in session state
    if 'agent_analysis_results' in st.session_state and st.session_state.agent_analysis_results:
        st.subheader("Latest Agent Analysis Results")
        for field_name, results in st.session_state.agent_analysis_results.items():
            with st.expander(f"Raw Results for {field_name}", expanded=False):
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
        st.subheader("Agent Insights and Anomalies")
        for field_name, insights in st.session_state.agent_processed_insights.items():
            with st.expander(f"Insights for {field_name}", expanded=True):
                st.write(f"**Summary:** {insights.get('summary', 'No summary available.')}")
                if insights.get('anomalies'):
                    st.write("**Anomalies Detected:**")
                    for anomaly in insights['anomalies']:
                        st.warning(f"- {anomaly}")
                else:
                    st.info("No significant anomalies detected.")

with tab5:
    st.header("Agricultural Chatbot")
    
    # Display chat messages from history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask me about your fields..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate the agent's response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ""
                
                # --- Chatbot Logic ---+
                
                # State 1: Idle or receiving a general query
                if st.session_state.chatbot_state == 'idle':
                    if any(keyword in prompt.lower() for keyword in ["health", "analysis", "report", "results", "insights"]):
                        if st.session_state.chatbot_field_coords:
                            response = f"Please wait while I analyze the field at coordinates {st.session_state.chatbot_field_coords[1]:.4f}, {st.session_state.chatbot_field_coords[0]:.4f}.\n\n" # Note: coordinates are [lon, lat] but we display lat, lon for user
                            
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
                                response += "Here is the analysis report for the requested field:\n\n"
                                response += f"**Summary:** {field_insights.get('summary', 'No summary available.')}\n"
                                if field_insights.get('anomalies'):
                                    response += "**Anomalies Detected:**\n"
                                    for anomaly in field_insights['anomalies']:
                                        response += f"- {anomaly}\n"

                                # Add detailed recommendations
                                if 'recommendations' in analysis_results and analysis_results['recommendations']:
                                    recommendations = analysis_results['recommendations']
                                    response += "\n**Detailed Recommendations:**\n"
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
                            response = "I can help with that! Please provide the coordinates of the farm you'd like to analyze (e.g., 38.5, -121.7)."
                            st.session_state.chatbot_state = 'awaiting_coords'
                            
                    elif any(keyword in prompt.lower() for keyword in ["hello", "hi", "hey"]):
                         response = "Hello! I am your agricultural assistant chatbot. How can I help you today? You can ask me about analyzing a field's health or managing your monitored fields."

                    else:
                        response = "I'm not sure how to help with that. You can ask me to 'analyze a field' or provide a 'report' on a specific location."
                        
                # State 2: Awaiting coordinates
                elif st.session_state.chatbot_state == 'awaiting_coords':
                    coords = parse_coordinates(prompt)
                    if coords:
                        st.session_state.chatbot_field_coords = coords
                        st.session_state.chatbot_state = 'idle' # Move back to idle after getting coords
                        response = f"Thank you! I have the coordinates: {coords[1]:.4f}, {coords[0]:.4f}. Now, what would you like to know about this field? You can ask for an 'analysis' or 'report'."
                        
                        # Optionally, trigger analysis immediately after getting coordinates
                        # if any(keyword in prompt.lower() for keyword in ["health", "analysis", "report", "results", "insights"]):
                        #     # Code to trigger analysis and display report here
                        #     pass # We will add this logic in the next step
                            
                    else:
                        response = "I couldn't understand the coordinates. Please provide them in a format like 'latitude, longitude' (e.g., 38.5, -121.7)."

                else:
                     response = "An unexpected error occurred with the chatbot state."

                # --- End Chatbot Logic ---+

                st.markdown(response)

        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

st.sidebar.markdown("---")
st.sidebar.info("Developed for sustainable farming 🌾") 