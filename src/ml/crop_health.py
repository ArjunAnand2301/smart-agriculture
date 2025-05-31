import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from pathlib import Path

class CropHealthAnalyzer:
    def __init__(self):
        """Initialize the Crop Health Analyzer."""
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = Path('models/crop_health_model.joblib')
        self.scaler_path = Path('models/crop_health_scaler.joblib')
        self._load_or_create_model()

    def _load_or_create_model(self):
        """Load existing model or create a new one if it doesn't exist."""
        try:
            if self.model_path.exists() and self.scaler_path.exists():
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
            else:
                # Create a new model
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                # Save the new model
                os.makedirs('models', exist_ok=True)
                joblib.dump(self.model, self.model_path)
                joblib.dump(self.scaler, self.scaler_path)
        except Exception as e:
            print(f"Error loading/creating model: {str(e)}")
            raise

    def analyze(self, imagery_data):
        """
        Analyze crop health using satellite imagery data.
        
        Args:
            imagery_data (dict): Satellite imagery data from image_processor
            
        Returns:
            dict: Analysis results including health score and recommendations
        """
        try:
            # Check if we're using placeholder data
            status = imagery_data.get('metadata', {}).get('status', '')
            if 'placeholder' in status.lower() or 'error' in status.lower():
                # Generate analysis based on available data or defaults
                health_score = 0.5  # Default moderate health score
                recommendations = [
                    "Limited satellite data available for analysis",
                    "Consider ground-based monitoring",
                    "Review historical field performance",
                    "Check local weather conditions"
                ]
                
                if 'No valid image found' in status:
                    recommendations.append("Try adjusting the date range for analysis")
                elif 'Missing required bands' in status:
                    recommendations.append("Satellite data quality issues detected")
                
                return {
                    'health_score': health_score,
                    'health_status': self._get_health_status(health_score),
                    'recommendations': recommendations,
                    'data_quality': 'limited',
                    'status_message': status
                }
            
            # Extract features from imagery
            features = self._extract_features(imagery_data)
            
            # Fit the scaler on the current features for demo/testing
            self.scaler.fit(features.reshape(1, -1))
            # Scale features
            scaled_features = self.scaler.transform(features.reshape(1, -1))
            
            # Get health prediction
            health_score = self._predict_health_score(scaled_features)
            
            # Generate analysis results
            analysis = {
                'health_score': float(health_score),
                'health_status': self._get_health_status(health_score),
                'recommendations': self._generate_recommendations(health_score, features),
                'data_quality': 'good',
                'status_message': 'Analysis completed successfully'
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing crop health: {str(e)}")
            # Return a basic analysis in case of errors
            return {
                'health_score': 0.5,
                'health_status': 'Unknown',
                'recommendations': [
                    "Error in analysis",
                    "Please try again later",
                    "Consider manual field inspection"
                ],
                'data_quality': 'error',
                'status_message': f'Error in analysis: {str(e)}'
            }

    def _extract_features(self, imagery_data):
        """
        Extract relevant features from satellite imagery.
        
        Args:
            imagery_data (dict): Satellite imagery data
            
        Returns:
            numpy.ndarray: Extracted features
        """
        try:
            # In a real implementation, this would process the actual image data
            # For demonstration, we'll create some synthetic features
            features = np.array([
                imagery_data.get('metadata', {}).get('cloud_coverage', 0),
                np.mean(imagery_data.get('image', np.zeros((100, 100, 3)))),
                np.std(imagery_data.get('image', np.zeros((100, 100, 3))))
            ])
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            raise

    def _predict_health_score(self, features):
        """
        Predict crop health score using the trained model.
        
        Args:
            features (numpy.ndarray): Scaled features
            
        Returns:
            float: Predicted health score (0-1)
        """
        try:
            # In a real implementation, this would use the actual trained model
            # For demonstration, we'll return a synthetic score
            return np.clip(np.mean(features) + 0.5, 0, 1)
            
        except Exception as e:
            print(f"Error predicting health score: {str(e)}")
            raise

    def _get_health_status(self, health_score):
        """
        Convert health score to status category.
        
        Args:
            health_score (float): Health score between 0 and 1
            
        Returns:
            str: Health status category
        """
        if health_score >= 0.8:
            return "Excellent"
        elif health_score >= 0.6:
            return "Good"
        elif health_score >= 0.4:
            return "Fair"
        else:
            return "Poor"

    def _generate_recommendations(self, health_score, features):
        """
        Generate recommendations based on health score and features.
        
        Args:
            health_score (float): Health score between 0 and 1
            features (numpy.ndarray): Extracted features
            
        Returns:
            list: List of recommendations
        """
        recommendations = []
        
        # Add recommendations based on health score
        if health_score < 0.4:
            recommendations.extend([
                "Consider increasing irrigation frequency",
                "Check for pest infestation",
                "Monitor soil nutrient levels"
            ])
        elif health_score < 0.6:
            recommendations.extend([
                "Maintain current irrigation schedule",
                "Consider light fertilization",
                "Monitor crop growth patterns"
            ])
        elif health_score < 0.8:
            recommendations.extend([
                "Continue current management practices",
                "Schedule regular health checks",
                "Consider preventive pest control"
            ])
        else:
            recommendations.extend([
                "Maintain optimal conditions",
                "Continue regular monitoring",
                "Document successful practices"
            ])
        
        # Add specific recommendations based on features
        if features[0] > 0.5:  # High cloud coverage
            recommendations.append("Consider additional ground-based monitoring")
        
        if features[1] < 0.3:  # Low mean value
            recommendations.append("Consider soil enrichment")
        
        if features[2] > 0.7:  # High standard deviation
            recommendations.append("Investigate field variability")
        
        return recommendations

    def get_detailed_analysis(self, coordinates):
        """
        Get detailed analysis for a specific location.
        
        Args:
            coordinates (list): [longitude, latitude]
            
        Returns:
            dict: Detailed analysis results
        """
        try:
            # In a real implementation, this would get actual data for the location
            # For demonstration, we'll return synthetic data
            return {
                'location': coordinates,
                'soil_quality': np.random.uniform(0.5, 0.9),
                'water_stress': np.random.uniform(0.1, 0.5),
                'nutrient_levels': {
                    'nitrogen': np.random.uniform(0.4, 0.8),
                    'phosphorus': np.random.uniform(0.4, 0.8),
                    'potassium': np.random.uniform(0.4, 0.8)
                },
                'pest_pressure': np.random.uniform(0.1, 0.4),
                'disease_risk': np.random.uniform(0.1, 0.3)
            }
            
        except Exception as e:
            print(f"Error getting detailed analysis: {str(e)}")
            raise 