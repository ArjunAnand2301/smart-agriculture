import numpy as np
from datetime import datetime, timedelta

class ResourceOptimizer:
    def __init__(self):
        """Initialize the Resource Optimizer."""
        self.water_thresholds = {
            'critical': 0.3,
            'low': 0.5,
            'optimal': 0.7,
            'high': 0.9
        }
        
        self.pesticide_thresholds = {
            'critical': 0.4,
            'low': 0.6,
            'optimal': 0.8
        }

    def get_recommendations(self, health_analysis, coordinates):
        """
        Generate comprehensive resource optimization recommendations.
        
        Args:
            health_analysis (dict): Results from crop health analysis
            coordinates (list): [longitude, latitude]
            
        Returns:
            dict: Optimization recommendations
        """
        try:
            recommendations = {
                'water_management': self._get_water_recommendations(health_analysis),
                'pesticide_management': self._get_pesticide_recommendations(health_analysis),
                'fertilizer_management': self._get_fertilizer_recommendations(health_analysis),
                'general_recommendations': self._get_general_recommendations(health_analysis)
            }
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            raise

    def optimize_water_usage(self, soil_moisture, weather_data):
        """
        Optimize water usage based on soil moisture and weather data.
        
        Args:
            soil_moisture (float): Current soil moisture level (0-1)
            weather_data (dict): Weather forecast data
            
        Returns:
            dict: Water usage recommendations
        """
        try:
            recommendations = {
                'irrigation_schedule': self._calculate_irrigation_schedule(soil_moisture, weather_data),
                'water_amount': self._calculate_water_amount(soil_moisture, weather_data),
                'efficiency_tips': self._get_water_efficiency_tips(soil_moisture)
            }
            
            return recommendations
            
        except Exception as e:
            print(f"Error optimizing water usage: {str(e)}")
            raise

    def optimize_pesticide_usage(self, health_data, crop_type):
        """
        Optimize pesticide usage based on crop health and type.
        
        Args:
            health_data (dict): Detailed health analysis data
            crop_type (str): Type of crop being grown
            
        Returns:
            dict: Pesticide usage recommendations
        """
        try:
            recommendations = {
                'application_schedule': self._calculate_pesticide_schedule(health_data, crop_type),
                'pesticide_type': self._recommend_pesticide_type(health_data, crop_type),
                'application_amount': self._calculate_pesticide_amount(health_data, crop_type),
                'safety_measures': self._get_pesticide_safety_measures(crop_type)
            }
            
            return recommendations
            
        except Exception as e:
            print(f"Error optimizing pesticide usage: {str(e)}")
            raise

    def _get_water_recommendations(self, health_analysis):
        """Generate water management recommendations."""
        health_score = health_analysis.get('health_score', 0.5)
        
        if health_score < 0.4:
            return {
                'action': 'Increase',
                'schedule': 'Daily',
                'amount': 'High',
                'reason': 'Poor crop health indicates water stress'
            }
        elif health_score < 0.6:
            return {
                'action': 'Maintain',
                'schedule': 'Every 2-3 days',
                'amount': 'Medium',
                'reason': 'Moderate crop health requires regular irrigation'
            }
        else:
            return {
                'action': 'Optimize',
                'schedule': 'As needed',
                'amount': 'Low',
                'reason': 'Good crop health indicates adequate water'
            }

    def _get_pesticide_recommendations(self, health_analysis):
        """Generate pesticide management recommendations."""
        health_score = health_analysis.get('health_score', 0.5)
        
        if health_score < 0.4:
            return {
                'action': 'Apply',
                'schedule': 'Immediate',
                'type': 'Broad-spectrum',
                'reason': 'Poor crop health indicates potential pest issues'
            }
        elif health_score < 0.6:
            return {
                'action': 'Monitor',
                'schedule': 'Weekly',
                'type': 'Targeted',
                'reason': 'Moderate crop health requires careful monitoring'
            }
        else:
            return {
                'action': 'Preventive',
                'schedule': 'As needed',
                'type': 'Organic',
                'reason': 'Good crop health allows for preventive measures'
            }

    def _get_fertilizer_recommendations(self, health_analysis):
        """Generate fertilizer management recommendations."""
        health_score = health_analysis.get('health_score', 0.5)
        
        if health_score < 0.4:
            return {
                'action': 'Apply',
                'type': 'Balanced NPK',
                'amount': 'High',
                'schedule': 'Immediate'
            }
        elif health_score < 0.6:
            return {
                'action': 'Supplement',
                'type': 'Targeted nutrients',
                'amount': 'Medium',
                'schedule': 'Weekly'
            }
        else:
            return {
                'action': 'Maintain',
                'type': 'Slow-release',
                'amount': 'Low',
                'schedule': 'Monthly'
            }

    def _get_general_recommendations(self, health_analysis):
        """Generate general farming recommendations."""
        health_score = health_analysis.get('health_score', 0.5)
        
        recommendations = []
        
        if health_score < 0.4:
            recommendations.extend([
                "Conduct soil testing",
                "Review irrigation system",
                "Check for drainage issues",
                "Monitor pest activity"
            ])
        elif health_score < 0.6:
            recommendations.extend([
                "Maintain regular monitoring",
                "Document crop growth",
                "Review fertilization schedule",
                "Check irrigation efficiency"
            ])
        else:
            recommendations.extend([
                "Continue current practices",
                "Document successful methods",
                "Plan for next season",
                "Consider crop rotation"
            ])
        
        return recommendations

    def _calculate_irrigation_schedule(self, soil_moisture, weather_data):
        """Calculate optimal irrigation schedule."""
        if soil_moisture < self.water_thresholds['critical']:
            return "Daily"
        elif soil_moisture < self.water_thresholds['low']:
            return "Every 2-3 days"
        elif soil_moisture < self.water_thresholds['optimal']:
            return "Weekly"
        else:
            return "As needed"

    def _calculate_water_amount(self, soil_moisture, weather_data):
        """Calculate recommended water amount."""
        base_amount = 0.5  # Base amount in inches
        
        # Adjust based on soil moisture
        if soil_moisture < self.water_thresholds['critical']:
            multiplier = 1.5
        elif soil_moisture < self.water_thresholds['low']:
            multiplier = 1.2
        elif soil_moisture < self.water_thresholds['optimal']:
            multiplier = 1.0
        else:
            multiplier = 0.8
        
        # Adjust based on weather
        if weather_data.get('temperature', 25) > 30:
            multiplier *= 1.2
        if weather_data.get('precipitation', 0) > 0:
            multiplier *= 0.5
        
        return round(base_amount * multiplier, 2)

    def _get_water_efficiency_tips(self, soil_moisture):
        """Generate water efficiency tips."""
        tips = [
            "Use drip irrigation for targeted watering",
            "Water during early morning or evening",
            "Monitor soil moisture regularly",
            "Implement mulching to retain moisture"
        ]
        
        if soil_moisture < self.water_thresholds['low']:
            tips.append("Consider installing moisture sensors")
        
        return tips

    def _calculate_pesticide_schedule(self, health_data, crop_type):
        """Calculate optimal pesticide application schedule."""
        pest_pressure = health_data.get('pest_pressure', 0.5)
        
        if pest_pressure > 0.7:
            return "Immediate application"
        elif pest_pressure > 0.5:
            return "Weekly monitoring and application as needed"
        else:
            return "Monthly preventive application"

    def _recommend_pesticide_type(self, health_data, crop_type):
        """Recommend appropriate pesticide type."""
        pest_pressure = health_data.get('pest_pressure', 0.5)
        disease_risk = health_data.get('disease_risk', 0.5)
        
        if pest_pressure > 0.7 or disease_risk > 0.7:
            return "Broad-spectrum pesticide"
        elif pest_pressure > 0.5 or disease_risk > 0.5:
            return "Targeted pesticide"
        else:
            return "Organic preventive treatment"

    def _calculate_pesticide_amount(self, health_data, crop_type):
        """Calculate recommended pesticide amount."""
        pest_pressure = health_data.get('pest_pressure', 0.5)
        base_amount = 1.0  # Base amount in liters per hectare
        
        if pest_pressure > 0.7:
            return round(base_amount * 1.2, 2)
        elif pest_pressure > 0.5:
            return round(base_amount * 1.0, 2)
        else:
            return round(base_amount * 0.8, 2)

    def _get_pesticide_safety_measures(self, crop_type):
        """Generate pesticide safety measures."""
        return [
            "Wear appropriate protective equipment",
            "Follow label instructions carefully",
            "Apply during calm weather conditions",
            "Keep records of applications",
            "Store pesticides securely",
            "Dispose of containers properly"
        ] 