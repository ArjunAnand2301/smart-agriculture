import json
from datetime import datetime, timedelta
from src.main import SmartAgricultureSystem

def test_system():
    """Test the main smart agriculture system with a real field location."""
    try:
        print("Initializing Smart Agriculture System...")
        system = SmartAgricultureSystem()
        
        # Example field coordinates (you can replace these with your actual field coordinates)
        # This is an example field in California's Central Valley
        field_coordinates = [-121.7421, 38.5449]  # Davis, CA (agricultural area)
        
        # Get dates for analysis (last 30 days)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"\nAnalyzing field at coordinates: {field_coordinates}")
        print(f"Analysis period: {start_date} to {end_date}")
        
        # 1. Analyze field health
        print("\n1. Analyzing field health...")
        results = system.analyze_field(field_coordinates, start_date, end_date)
        print("\nField Analysis Results:")
        print(json.dumps(results, indent=2))
        
        # 2. Get water usage recommendations
        print("\n2. Getting water usage recommendations...")
        weather_data = {
            'temperature': 25,  # Celsius
            'humidity': 60,     # Percentage
            'precipitation': 0  # mm
        }
        water_recommendations = system.get_water_usage_recommendations(
            field_coordinates,
            weather_data
        )
        print("\nWater Usage Recommendations:")
        print(json.dumps(water_recommendations, indent=2))
        
        # 3. Get pesticide recommendations
        print("\n3. Getting pesticide recommendations...")
        pesticide_recommendations = system.get_pesticide_recommendations(
            field_coordinates,
            'wheat'  # Example crop type
        )
        print("\nPesticide Usage Recommendations:")
        print(json.dumps(pesticide_recommendations, indent=2))
        
        print("\nSystem test completed successfully! ✅")
        return True
        
    except Exception as e:
        print(f"\nError testing system: {str(e)}")
        print("System test FAILED! ❌")
        return False

if __name__ == "__main__":
    test_system() 