import ee
import numpy as np
from datetime import datetime
import rasterio
from rasterio.transform import from_origin
import os

class SatelliteImageProcessor:
    def __init__(self):
        """Initialize the Satellite Image Processor."""
        self.sentinel_collection = 'COPERNICUS/S2_SR'  # Sentinel-2 Surface Reflectance
        self.landsat_collection = 'LANDSAT/LC08/C02/T1_L2'  # Landsat 8 Surface Reflectance (new version)

    def get_satellite_imagery(self, coordinates, start_date, end_date, buffer_meters=1000):
        """
        Get satellite imagery for a specific location and time period.
        
        Args:
            coordinates (list): [longitude, latitude]
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            buffer_meters (int): Buffer around the point of interest
            
        Returns:
            dict: Processed satellite imagery data
        """
        try:
            # Create a point geometry
            point = ee.Geometry.Point(coordinates)
            region = point.buffer(buffer_meters)
            
            # Get Sentinel-2 imagery
            sentinel = ee.ImageCollection(self.sentinel_collection) \
                .filterBounds(region) \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .sort('CLOUDY_PIXEL_PERCENTAGE') \
                .first()
            
            # Check if we got a valid image
            if sentinel is None:
                print(f"No valid Sentinel-2 image found for coordinates {coordinates} between {start_date} and {end_date}")
                # Return a default image with placeholder data
                return {
                    'image': np.zeros((100, 100, 3)),
                    'metadata': {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'cloud_coverage': 0,
                        'bands': ['B2', 'B3', 'B4'],
                        'center_lat': coordinates[1],
                        'center_lon': coordinates[0],
                        'status': 'No valid image found, using placeholder data'
                    }
                }
            
            # Verify that the image has the required bands
            required_bands = ['B2', 'B3', 'B4', 'B8']
            available_bands = sentinel.bandNames().getInfo()
            missing_bands = [band for band in required_bands if band not in available_bands]
            
            if missing_bands:
                print(f"Warning: Image missing required bands: {missing_bands}")
                # Return a default image with placeholder data
                return {
                    'image': np.zeros((100, 100, 3)),
                    'metadata': {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'cloud_coverage': 0,
                        'bands': available_bands,
                        'center_lat': coordinates[1],
                        'center_lon': coordinates[0],
                        'status': f'Missing required bands: {missing_bands}, using placeholder data'
                    }
                }
            
            try:
                # Calculate NDVI (Normalized Difference Vegetation Index)
                ndvi = sentinel.normalizedDifference(['B8', 'B4']).rename('NDVI')
                
                # Calculate NDWI (Normalized Difference Water Index)
                ndwi = sentinel.normalizedDifference(['B3', 'B8']).rename('NDWI')
                
                # Combine all bands and indices
                image = sentinel.addBands([ndvi, ndwi])
                
                # Get the image data
                image_data = self._download_image(image, region)
                
                return {
                    'image': image_data,
                    'metadata': {
                        'date': sentinel.get('system:time_start').getInfo(),
                        'cloud_coverage': sentinel.get('CLOUDY_PIXEL_PERCENTAGE').getInfo(),
                        'bands': sentinel.bandNames().getInfo(),
                        'center_lat': coordinates[1],
                        'center_lon': coordinates[0],
                        'status': 'success'
                    }
                }
            except Exception as e:
                print(f"Error processing satellite image: {str(e)}")
                # Return a default image with placeholder data
                return {
                    'image': np.zeros((100, 100, 3)),
                    'metadata': {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'cloud_coverage': 0,
                        'bands': available_bands,
                        'center_lat': coordinates[1],
                        'center_lon': coordinates[0],
                        'status': f'Error processing image: {str(e)}, using placeholder data'
                    }
                }
            
        except Exception as e:
            print(f"Error getting satellite imagery: {str(e)}")
            # Return a default image with placeholder data
            return {
                'image': np.zeros((100, 100, 3)),
                'metadata': {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'cloud_coverage': 0,
                    'bands': ['B2', 'B3', 'B4'],
                    'center_lat': coordinates[1],
                    'center_lon': coordinates[0],
                    'status': f'Error: {str(e)}, using placeholder data'
                }
            }

    def get_soil_moisture(self, coordinates, buffer_meters=1000):
        """
        Estimate soil moisture using satellite data.
        
        Args:
            coordinates (list): [longitude, latitude]
            buffer_meters (int): Buffer around the point of interest
            
        Returns:
            float: Estimated soil moisture index
        """
        try:
            point = ee.Geometry.Point(coordinates)
            region = point.buffer(buffer_meters)
            
            # Get recent Landsat 8 imagery (using new collection)
            landsat = ee.ImageCollection(self.landsat_collection) \
                .filterBounds(region) \
                .filterDate(
                    ee.Date(datetime.now()).advance(-7, 'day'),
                    ee.Date(datetime.now())
                ) \
                .sort('CLOUD_COVER') \
                .first()
            
            # Check if we got a valid image
            if landsat is None:
                print("No Landsat image found for the specified region and date range")
                return 0.5  # Return a default value
            
            # In the new collection (LC08/C02/T1_L2), band names are:
            # Green: SR_B3
            # SWIR: SR_B6
            # First, select the bands we need
            landsat = landsat.select(['SR_B3', 'SR_B6'])
            
            # Calculate Modified Normalized Difference Water Index (MNDWI)
            mndwi = landsat.normalizedDifference(['SR_B3', 'SR_B6']).rename('MNDWI')
            
            # Get the MNDWI value for the region
            mndwi_value = mndwi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=30
            ).get('MNDWI').getInfo()
            
            if mndwi_value is None:
                print("Could not calculate MNDWI value")
                return 0.5  # Return a default value
            
            # Convert MNDWI to soil moisture index (0-1 scale)
            soil_moisture = (mndwi_value + 1) / 2
            
            return soil_moisture
            
        except Exception as e:
            print(f"Error calculating soil moisture: {str(e)}")
            return 0.5  # Return a default value in case of error

    def _download_image(self, image, region, scale=10):
        """
        Download and process Earth Engine image to numpy array.
        
        Args:
            image (ee.Image): Earth Engine image
            region (ee.Geometry): Region of interest
            scale (int): Pixel scale in meters
            
        Returns:
            numpy.ndarray: Processed image data
        """
        try:
            # Select only RGB bands for visualization
            image = image.select(['B4', 'B3', 'B2'])
            # Get the image URL
            url = image.getThumbURL({
                'region': region,
                'scale': scale,
                'format': 'png'
            })
            # Download and process the image
            # Note: In a real implementation, you would need to handle the actual download
            # and processing of the image data. This is a simplified version.
            # For demonstration, return a placeholder array
            return np.zeros((100, 100, 3))  # Placeholder
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            raise

    def calculate_vegetation_indices(self, image):
        """
        Calculate various vegetation indices from satellite imagery.
        
        Args:
            image (ee.Image): Earth Engine image
            
        Returns:
            dict: Dictionary of vegetation indices
        """
        try:
            # Calculate NDVI
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            
            # Calculate EVI (Enhanced Vegetation Index)
            evi = image.expression(
                '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
                {
                    'NIR': image.select('B8'),
                    'RED': image.select('B4'),
                    'BLUE': image.select('B2')
                }
            ).rename('EVI')
            
            # Calculate SAVI (Soil Adjusted Vegetation Index)
            savi = image.expression(
                '((NIR - RED) * (1 + L)) / (NIR + RED + L)',
                {
                    'NIR': image.select('B8'),
                    'RED': image.select('B4'),
                    'L': 0.5
                }
            ).rename('SAVI')
            
            return {
                'ndvi': ndvi,
                'evi': evi,
                'savi': savi
            }
            
        except Exception as e:
            print(f"Error calculating vegetation indices: {str(e)}")
            raise 