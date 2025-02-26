import geopandas as gpd
import json
import requests
import os
import numpy as np
from shapely.geometry import shape, Point
import pandas as pd
import tempfile
import subprocess
import sys

class GeoConverter:
    """
    Class for converting TopoJSON to GeoJSON and handling geographic data.
    """
    
    def __init__(self):
        """Initialize the GeoConverter."""
        self.data = None
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
                # Download the TopoJSON data
                response = requests.get(topojson_url)
                data = json.loads(response.text)
                
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
    
    def convert_to_geodataframe(self):
        """
        Convert the loaded TopoJSON to a GeoDataFrame.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.data:
            print("No data loaded. Call load_topojson() first.")
            return False
        
        # Try multiple methods to convert TopoJSON to GeoJSON
        
        # Method 1: Try to read directly with GeoPandas
        try:
            print("Method 1: Attempting to read TopoJSON directly with GeoPandas...")
            
            # # Save TopoJSON to a temporary file
            # with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            #     tmp_path = tmp.name
            #     json.dump(self.data, tmp)
            
            # # Try to read with GeoPandas
            # self.gdf = gpd.read_file(tmp_path)
            # os.unlink(tmp_path)  # Clean up temp file
            
            self.gdf = gpd.read_file()
            print("Successfully loaded data with GeoPandas")
            self._identify_name_column()
            return True
        except Exception as e:
            print(f"Method 1 failed: {e}")
            
            # Clean up temp file if it exists
            # try:
            #     if 'tmp_path' in locals():
            #         # os.unlink(tmp_path)
            # except:
            #     pass
        
        # # Method 2: Try using mapshaper CLI if available
        # try:
        #     print("Method 2: Attempting to convert using mapshaper CLI...")
            
        #     # Check if mapshaper is installed
        #     try:
        #         subprocess.run(['mapshaper', '--version'], 
        #                        stdout=subprocess.PIPE, 
        #                        stderr=subprocess.PIPE, 
        #                        check=True)
        #         mapshaper_available = True
        #     except:
        #         mapshaper_available = False
        #         print("Mapshaper not found. Install with: npm install -g mapshaper")
            
        #     if mapshaper_available:
        #         # Save TopoJSON to a temporary file
        #         with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        #             tmp_path = tmp.name
        #             json.dump(self.data, tmp)
                
        #         # Output GeoJSON path
        #         geojson_path = tmp_path + '.geojson'
                
        #         # Convert using mapshaper
        #         subprocess.run(['mapshaper', tmp_path, '-o', 'format=geojson', geojson_path], 
        #                        stdout=subprocess.PIPE, 
        #                        stderr=subprocess.PIPE, 
        #                        check=True)
                
        #         # Read the converted GeoJSON
        #         self.gdf = gpd.read_file(geojson_path)
                
        #         # Clean up temp files
        #         os.unlink(tmp_path)
        #         os.unlink(geojson_path)
                
        #         print("Successfully converted using mapshaper")
        #         self._identify_name_column()
        #         return True
        # except Exception as e:
        #     print(f"Method 2 failed: {e}")
            
        #     # Clean up temp files if they exist
        #     try:
        #         if 'tmp_path' in locals():
        #             os.unlink(tmp_path)
        #         if 'geojson_path' in locals() and os.path.exists(geojson_path):
        #             os.unlink(geojson_path)
        #     except:
        #         pass
        
        # # Method 3: Try using a direct URL to a GeoJSON version if available
        # try:
        #     print("Method 3: Attempting to find a GeoJSON equivalent URL...")
            
        #     # Try to modify the URL to point to a GeoJSON version
        #     # This is specific to the UK-GeoJSON repository structure
        #     if "topo_" in self.topojson_url:
        #         geojson_url = self.topojson_url.replace("topo_", "")
        #     else:
        #         # Try to extract the ID from the URL
        #         import re
        #         match = re.search(r'([A-Z][0-9]+)', self.topojson_url)
        #         if match:
        #             id_value = match.group(1)
        #             base_url = self.topojson_url.split(id_value)[0]
        #             geojson_url = f"{base_url}{id_value}.geojson"
        #         else:
        #             raise ValueError("Could not determine GeoJSON URL")
            
        #     # Try to load the GeoJSON URL
        #     self.gdf = gpd.read_file(geojson_url)
        #     print(f"Successfully loaded GeoJSON from {geojson_url}")
        #     self._identify_name_column()
        #     return True
        # except Exception as e:
        #     print(f"Method 3 failed: {e}")
        
        # # Method 4: Manual extraction of properties with placeholder geometries
        # print("Method 4: Creating a GeoDataFrame with properties and placeholder geometries...")
        # try:
        #     # Extract properties from TopoJSON
        #     properties_list = []
            
        #     for geometry in self.data['objects'][self.object_name]['geometries']:
        #         if 'properties' in geometry:
        #             props = geometry['properties'].copy()
                    
        #             # Add an ID if available
        #             if 'id' in geometry:
        #                 props['id'] = geometry['id']
                    
        #             properties_list.append(props)
            
        #     # Create a DataFrame with the properties
        #     df = pd.DataFrame(properties_list)
            
        #     # Create a GeoDataFrame with placeholder Point geometries
        #     # This is not ideal but allows us to at least have the properties
        #     self.gdf = gpd.GeoDataFrame(
        #         df, 
        #         geometry=[Point(0, 0) for _ in range(len(df))],
        #         crs="EPSG:4326"  # WGS84
        #     )
            
        #     print("Created GeoDataFrame with properties and placeholder geometries")
        #     print("WARNING: The geometries are placeholders and not actual geographic shapes")
            
        #     # Find the name column
        #     self._identify_name_column()
            
        #     return True
        # except Exception as e:
        #     print(f"Method 4 failed: {e}")
        #     return False
    
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
        
        # Use the first string column as a fallback
        for col in self.gdf.columns:
            if self.gdf[col].dtype == 'object' and col != 'geometry':
                self.name_column = col
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
            print("No GeoDataFrame available. Convert data first.")
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
    
    def merge_geojson_files(self, file_paths, output_path):
        """
        Merge multiple GeoJSON files into one.
        
        Args:
            file_paths: List of paths to GeoJSON files
            output_path: Path to save the merged GeoJSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read and combine all GeoJSON files
            gdfs = []
            for file_path in file_paths:
                gdf = gpd.read_file(file_path)
                gdfs.append(gdf)
            
            # Concatenate all GeoDataFrames
            merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
            
            # Save the merged GeoJSON
            merged_gdf.to_file(output_path, driver='GeoJSON')
            print(f"Merged GeoJSON saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error merging GeoJSON files: {e}")
            return False 