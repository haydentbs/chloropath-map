import geopandas as gpd
import json
import requests
import os
import pandas as pd

class GeoConverter:
    """
    Class for converting TopoJSON to GeoJSON and handling geographic data.
    """
    
    def __init__(self):
        """Initialize the GeoConverter."""
        self.gdf = None
        self.name_column = None
        self.gdfs = []  # List to store multiple GeoDataFrames
    
    def load_topojson(self, topojson_urls):
        """
        Load TopoJSON data from one or more URLs and append them together.
        
        Args:
            topojson_urls: URL or list of URLs to the TopoJSON data
            
        Returns:
            bool: True if at least one URL was successfully loaded, False otherwise
        """
        # Convert single URL to list for consistent handling
        if isinstance(topojson_urls, str):
            topojson_urls = [topojson_urls]
        
        print(f"Processing {len(topojson_urls)} TopoJSON URLs...")
        
        # Reset the list of GeoDataFrames
        self.gdfs = []
        success = False
        
        for topojson_url in topojson_urls:
            print(f"Downloading data from {topojson_url}...")
            
            try:
                # Try to read directly with GeoPandas
                gdf = gpd.read_file(topojson_url)
                
                # Store the GeoDataFrame
                self.gdfs.append(gdf)
                success = True
                
                print(f"Successfully loaded data from {topojson_url}")
            except Exception as e:
                print(f"Error loading TopoJSON from {topojson_url}: {e}")
        
        # If we have at least one successful GeoDataFrame, merge them
        if success:
            # Merge all GeoDataFrames into one
            if len(self.gdfs) == 1:
                self.gdf = self.gdfs[0]
            else:
                self.gdf = gpd.GeoDataFrame(pd.concat(self.gdfs, ignore_index=True))
            
            print(f"Created a GeoDataFrame with {len(self.gdf)} features from {len(self.gdfs)} sources")
            
            # Identify the name column
            self._identify_name_column()
            return True
        else:
            print("Failed to load any TopoJSON URLs.")
            return False
    
    def _identify_name_column(self):
        """Identify the name column in the GeoDataFrame."""
        if self.gdf is None:
            return
        
        # Find the name column
        for col in ['PCON13NM', 'name', 'NAME', 'constituency_name']:
            if col in self.gdf.columns:
                self.name_column = col
                return
        
        # Look for columns with 'name' in them
        name_cols = [col for col in self.gdf.columns if 'name' in col.lower()]
        if name_cols:
            self.name_column = name_cols[0]
            return
    
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
    
    def download_complete_uk_geojson(self, output_path):
        """
        Download a complete UK constituencies GeoJSON file.
        
        Args:
            output_path: Path to save the GeoJSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # URL to a complete UK constituencies GeoJSON
            uk_geojson_url = "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/electoral/eng/westminster/constituencies.geojson"
            
            print(f"Downloading complete UK constituencies from {uk_geojson_url}...")
            
            # Download and save directly
            gdf = gpd.read_file(uk_geojson_url)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            # Save to GeoJSON
            gdf.to_file(output_path, driver='GeoJSON')
            
            print(f"Complete UK constituencies GeoJSON saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error downloading complete UK GeoJSON: {e}")
            return False 