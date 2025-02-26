import geopandas as gpd
import json
import os
import pandas as pd
from shapely.geometry import Polygon, shape

class GeoConverter:
    """
    Class for converting custom JSON to GeoJSON and handling geographic data.
    """
    
    def __init__(self):
        """Initialize the GeoConverter."""
        self.gdf = None
        self.name_column = 'name'  # We know our custom JSON uses 'name'
        self.gdfs = []
    
    def load_topojson(self, json_path):
        """
        Load custom JSON data with area definitions.
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read the JSON file
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Convert the features to a GeoDataFrame
            features = data['features']
            
            # Create a list to store the data for the GeoDataFrame
            gdf_data = []
            
            for feature in features:
                # Extract the geometry and properties
                geometry = shape(feature['geometry'])
                properties = {
                    'name': feature['name'],
                    # Add any other properties you want to include
                }
                
                # Add to the list
                gdf_data.append({
                    'geometry': geometry,
                    **properties
                })
            
            # Create the GeoDataFrame
            self.gdf = gpd.GeoDataFrame(gdf_data, crs="EPSG:4326")
            print(f"Successfully loaded GeoJSON with {len(self.gdf)} regions")
            
            return True
            
        except Exception as e:
            print(f"Error loading JSON: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_geojson(self, output_path):
        """
        Save the GeoDataFrame as a GeoJSON file.
        
        Args:
            output_path: Path to save the GeoJSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.gdf is None:
            print("No GeoDataFrame available. Load data first.")
            return False
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            # Save to GeoJSON
            self.gdf.to_file(output_path, driver='GeoJSON')
            print(f"GeoJSON saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving GeoJSON: {e}")
            return False
    
    # def download_complete_uk_geojson(self, output_path):
    #     """
    #     Download a complete UK constituencies GeoJSON file.
        
    #     Args:
    #         output_path: Path to save the GeoJSON file
            
    #     Returns:
    #         bool: True if successful, False otherwise
    #     """
    #     try:
    #         # URL to a complete UK constituencies GeoJSON
    #         uk_geojson_url = "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/electoral/eng/westminster/constituencies.geojson"
            
    #         print(f"Downloading complete UK constituencies from {uk_geojson_url}...")
            
    #         # Download and save directly
    #         gdf = gpd.read_file(uk_geojson_url)
            
    #         # Ensure directory exists
    #         os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
    #         # Save to GeoJSON
    #         gdf.to_file(output_path, driver='GeoJSON')
            
    #         print(f"Complete UK constituencies GeoJSON saved to {output_path}")
    #         return True
    #     except Exception as e:
    #         print(f"Error downloading complete UK GeoJSON: {e}")
    #         return False 