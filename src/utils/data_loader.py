import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

class DataLoader:
    def __init__(self):
        """Initialize the Data Loader."""
        self.data_dir = Path('data')
        self.cache_dir = Path('data/cache')
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)

    def load_weather_data(self, coordinates, start_date, end_date):
        """
        Load weather data for a specific location and time period.
        
        Args:
            coordinates (list): [longitude, latitude]
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            dict: Weather data including temperature, humidity, and precipitation
        """
        try:
            # In a real implementation, this would fetch data from a weather API
            # For demonstration, we'll return synthetic data
            return {
                'temperature': np.random.normal(25, 5),  # Mean 25°C, std 5°C
                'humidity': np.random.normal(60, 10),    # Mean 60%, std 10%
                'precipitation': np.random.exponential(2)  # Mean 2mm
            }
        except Exception as e:
            print(f"Error loading weather data: {str(e)}")
            raise

    def load_soil_data(self, coordinates):
        """
        Load soil data for a specific location.
        
        Args:
            coordinates (list): [longitude, latitude]
            
        Returns:
            dict: Soil data including moisture, pH, and nutrient levels
        """
        try:
            # In a real implementation, this would fetch data from a soil database
            # For demonstration, we'll return synthetic data
            return {
                'moisture': np.random.uniform(0.3, 0.7),
                'ph': np.random.uniform(6.0, 7.5),
                'nutrients': {
                    'nitrogen': np.random.uniform(0.4, 0.8),
                    'phosphorus': np.random.uniform(0.4, 0.8),
                    'potassium': np.random.uniform(0.4, 0.8)
                }
            }
        except Exception as e:
            print(f"Error loading soil data: {str(e)}")
            raise

    def load_crop_data(self, crop_type):
        """
        Load crop-specific data.
        
        Args:
            crop_type (str): Type of crop
            
        Returns:
            dict: Crop-specific data including growth stages and requirements
        """
        try:
            # In a real implementation, this would fetch data from a crop database
            # For demonstration, we'll return synthetic data
            crop_data = {
                'wheat': {
                    'growth_stages': ['germination', 'tillering', 'stem_elongation', 'heading', 'ripening'],
                    'water_requirements': {'min': 0.4, 'optimal': 0.6, 'max': 0.8},
                    'temperature_range': {'min': 15, 'optimal': 20, 'max': 25},
                    'growing_season': {'start': '10-01', 'end': '06-30'}
                },
                'corn': {
                    'growth_stages': ['emergence', 'vegetative', 'tasseling', 'silking', 'maturity'],
                    'water_requirements': {'min': 0.5, 'optimal': 0.7, 'max': 0.9},
                    'temperature_range': {'min': 18, 'optimal': 25, 'max': 30},
                    'growing_season': {'start': '04-15', 'end': '09-30'}
                }
            }
            return crop_data.get(crop_type.lower(), {})
        except Exception as e:
            print(f"Error loading crop data: {str(e)}")
            raise

    def save_analysis_results(self, results, field_id):
        """
        Save analysis results to a JSON file.
        
        Args:
            results (dict): Analysis results to save
            field_id (str): Unique identifier for the field
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'analysis_{field_id}_{timestamp}.json'
            filepath = self.data_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"Analysis results saved to {filepath}")
            
        except Exception as e:
            print(f"Error saving analysis results: {str(e)}")
            raise

    def load_historical_data(self, field_id, start_date, end_date):
        """
        Load historical analysis data for a field.
        
        Args:
            field_id (str): Unique identifier for the field
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            list: Historical analysis results
        """
        try:
            results = []
            for file in self.data_dir.glob(f'analysis_{field_id}_*.json'):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        results.append(data)
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Error loading historical data: {str(e)}")
            raise 