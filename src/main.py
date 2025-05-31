import os
import ee
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import requests

# Import local modules
from src.satellite.image_processor import SatelliteImageProcessor
from src.ml.crop_health import CropHealthAnalyzer
from src.ml.resource_optimizer import ResourceOptimizer
from src.utils.data_loader import DataLoader
from src.utils.visualization import Visualizer

class WeatherAnalyzer:
    """Class to handle weather data analysis and forecasting."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, lat, lon):
        """Get current weather data for given coordinates."""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'  # Use metric units
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching current weather: {str(e)}")
            return None

    def get_forecast(self, lat, lon):
        """Get 5-day weather forecast with 3-hour intervals."""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching forecast: {str(e)}")
            return None

    def analyze_weather_data(self, lat, lon):
        """Analyze weather data and generate insights."""
        current = self.get_current_weather(lat, lon)
        forecast = self.get_forecast(lat, lon)
        
        if not current or not forecast:
            return {
                'status': 'error',
                'message': 'Unable to fetch weather data'
            }
        
        # Process current weather
        current_data = {
            'temperature': current['main']['temp'],
            'feels_like': current['main']['feels_like'],
            'humidity': current['main']['humidity'],
            'pressure': current['main']['pressure'],
            'wind_speed': current['wind']['speed'],
            'wind_direction': current['wind'].get('deg', 0),
            'weather_description': current['weather'][0]['description'],
            'clouds': current['clouds']['all'],
            'timestamp': datetime.fromtimestamp(current['dt'])
        }
        
        # Process forecast data
        forecast_data = []
        for item in forecast['list']:
            forecast_data.append({
                'timestamp': datetime.fromtimestamp(item['dt']),
                'temperature': item['main']['temp'],
                'humidity': item['main']['humidity'],
                'weather_description': item['weather'][0]['description'],
                'wind_speed': item['wind']['speed'],
                'precipitation': item.get('pop', 0) * 100  # Probability of precipitation
            })
        
        # Generate insights
        insights = self._generate_weather_insights(current_data, forecast_data)
        
        return {
            'status': 'success',
            'current_weather': current_data,
            'forecast': forecast_data,
            'insights': insights
        }
    
    def _generate_weather_insights(self, current, forecast):
        """Generate insights from weather data."""
        insights = []
        
        # Temperature insights
        avg_temp = sum(f['temperature'] for f in forecast[:8]) / 8  # Average for next 24 hours
        if avg_temp > 30:
            insights.append("High temperatures expected. Consider additional irrigation.")
        elif avg_temp < 5:
            insights.append("Low temperatures expected. Monitor for frost damage.")
        
        # Precipitation insights
        total_precip_prob = sum(f['precipitation'] for f in forecast[:8]) / 8
        if total_precip_prob > 70:
            insights.append("High probability of precipitation. Plan irrigation accordingly.")
        
        # Wind insights
        if current['wind_speed'] > 20:
            insights.append("Strong winds detected. Consider wind protection measures.")
        
        # Humidity insights
        if current['humidity'] > 80:
            insights.append("High humidity levels. Monitor for disease development.")
        elif current['humidity'] < 30:
            insights.append("Low humidity levels. Consider additional irrigation.")
        
        return insights

class SmartAgricultureSystem:
    def __init__(self):
        """Initialize the Smart Agriculture System."""
        load_dotenv()
        self._initialize_earth_engine()
        self.image_processor = SatelliteImageProcessor()
        self.crop_health = CropHealthAnalyzer()
        self.resource_optimizer = ResourceOptimizer()
        self.data_loader = DataLoader()
        self.visualizer = Visualizer()
        self.weather_analyzer = WeatherAnalyzer()

    def _initialize_earth_engine(self):
        """Initialize Google Earth Engine with credentials."""
        try:
            credentials_path = os.getenv('EARTH_ENGINE_CREDENTIALS')
            if credentials_path and os.path.exists(credentials_path):
                credentials = ee.ServiceAccountCredentials(
                    os.getenv('EARTH_ENGINE_SERVICE_ACCOUNT'),
                    credentials_path
                )
                ee.Initialize(credentials)
            else:
                ee.Initialize()
            print("Earth Engine initialized successfully")
        except Exception as e:
            print(f"Error initializing Earth Engine: {str(e)}")
            raise

    def analyze_field(self, field_coordinates, start_date, end_date):
        """
        Analyze a specific field using satellite imagery and ML models.
        
        Args:
            field_coordinates (list): List of [longitude, latitude] coordinates
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
        """
        try:
            # Get satellite imagery
            imagery = self.image_processor.get_satellite_imagery(
                field_coordinates,
                start_date,
                end_date
            )
            
            # Analyze crop health
            health_analysis = self.crop_health.analyze(imagery)
            
            # Generate resource optimization recommendations
            recommendations = self.resource_optimizer.get_recommendations(
                health_analysis,
                field_coordinates
            )
            
            # Visualize results
            self.visualizer.create_analysis_visualization(
                imagery,
                health_analysis,
                recommendations
            )
            
            return {
                'health_analysis': health_analysis,
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"Error analyzing field: {str(e)}")
            raise

    def get_water_usage_recommendations(self, field_coordinates, weather_data):
        """
        Generate water usage recommendations based on field conditions and weather.
        
        Args:
            field_coordinates (list): List of [longitude, latitude] coordinates
            weather_data (dict): Weather forecast data
        """
        try:
            soil_moisture = self.image_processor.get_soil_moisture(field_coordinates)
            recommendations = self.resource_optimizer.optimize_water_usage(
                soil_moisture,
                weather_data
            )
            return recommendations
        except Exception as e:
            print(f"Error generating water recommendations: {str(e)}")
            raise

    def get_pesticide_recommendations(self, field_coordinates, crop_type):
        """
        Generate pesticide usage recommendations based on crop health and type.
        
        Args:
            field_coordinates (list): List of [longitude, latitude] coordinates
            crop_type (str): Type of crop being grown
        """
        try:
            health_data = self.crop_health.get_detailed_analysis(field_coordinates)
            recommendations = self.resource_optimizer.optimize_pesticide_usage(
                health_data,
                crop_type
            )
            return recommendations
        except Exception as e:
            print(f"Error generating pesticide recommendations: {str(e)}")
            raise

    def get_weather_report(self, coordinates, days=5):
        """Get comprehensive weather report for the given location."""
        try:
            weather_data = self.weather_analyzer.analyze_weather_data(coordinates[0], coordinates[1])
            return weather_data
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error generating weather report: {str(e)}'
            }

def main():
    """Main function to demonstrate the system's capabilities."""
    # Example usage
    system = SmartAgricultureSystem()
    
    # Example field coordinates (replace with actual coordinates)
    field_coordinates = [-122.4194, 37.7749]  # Example: San Francisco
    
    # Get current date and date 30 days ago
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        # Analyze field
        results = system.analyze_field(field_coordinates, start_date, end_date)
        print("\nField Analysis Results:")
        print(json.dumps(results, indent=2))
        
        # Get water usage recommendations
        weather_data = {
            'temperature': 25,
            'humidity': 60,
            'precipitation': 0
        }
        water_recommendations = system.get_water_usage_recommendations(
            field_coordinates,
            weather_data
        )
        print("\nWater Usage Recommendations:")
        print(json.dumps(water_recommendations, indent=2))
        
        # Get pesticide recommendations
        pesticide_recommendations = system.get_pesticide_recommendations(
            field_coordinates,
            'wheat'
        )
        print("\nPesticide Usage Recommendations:")
        print(json.dumps(pesticide_recommendations, indent=2))
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 