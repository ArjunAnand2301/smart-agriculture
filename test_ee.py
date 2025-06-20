# Create a test file: test_ee.py
import ee

try:
    ee.Initialize()
    print("Earth Engine initialized successfully!")
except Exception as e:
    print(f"Error initializing Earth Engine: {str(e)}")