import os
import ee
from dotenv import load_dotenv

def test_earth_engine():
    """Test Earth Engine authentication and basic functionality."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize Earth Engine
        credentials_path = os.getenv('EARTH_ENGINE_CREDENTIALS')
        service_account = os.getenv('EARTH_ENGINE_SERVICE_ACCOUNT')
        
        print("Initializing Earth Engine...")
        print(f"Using credentials from: {credentials_path}")
        print(f"Service account: {service_account}")
        
        # Initialize with credentials
        credentials = ee.ServiceAccountCredentials(service_account, credentials_path)
        ee.Initialize(credentials)
        
        # Test basic functionality
        print("\nTesting Earth Engine functionality...")
        
        # Get a sample Sentinel-2 image
        point = ee.Geometry.Point([-122.4194, 37.7749])  # San Francisco
        sentinel = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterBounds(point) \
            .filterDate('2024-01-01', '2024-05-30') \
            .first()
        
        # Get image properties
        properties = sentinel.getInfo()
        print("\nSuccessfully retrieved satellite image!")
        print(f"Image ID: {properties.get('id', 'N/A')}")
        print(f"Date: {properties.get('properties', {}).get('system:time_start', 'N/A')}")
        
        print("\nEarth Engine authentication and basic functionality test PASSED! ✅")
        return True
        
    except Exception as e:
        print(f"\nError testing Earth Engine: {str(e)}")
        print("Earth Engine test FAILED! ❌")
        return False

if __name__ == "__main__":
    test_earth_engine() 