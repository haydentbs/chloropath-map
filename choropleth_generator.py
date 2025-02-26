import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

class ChoroplethGenerator:
    """
    Class for generating choropleth maps and data visualizations.
    """
    
    def __init__(self):
        """Initialize the ChoroplethGenerator."""
        self.gdf = None
        self.name_column = None
        self.data_column = None
    
    def load_geojson(self, geojson_path):
        """
        Load GeoJSON data from a file.
        
        Args:
            geojson_path: Path to the GeoJSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read the GeoJSON
            self.gdf = gpd.read_file(geojson_path)
            print(f"Successfully loaded GeoJSON with {len(self.gdf)} regions")
            
            # Find the name column
            self._identify_name_column()
            
            return True
        except Exception as e:
            print(f"Error loading GeoJSON: {e}")
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
    
    def add_data(self, data_values, data_column_name='choropleth_value'):
        """
        Add data values to the GeoDataFrame for choropleth visualization.
        
        Args:
            data_values: Dictionary mapping region names to values
            data_column_name: Name for the data column
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.gdf is None or self.name_column is None:
            print("GeoDataFrame not properly loaded or name column not identified.")
            return False
        
        try:
            # Create the data column
            self.data_column = data_column_name
            self.gdf[self.data_column] = np.nan
            
            # Fill in values from the data_values dictionary
            for idx, row in self.gdf.iterrows():
                region_name = row[self.name_column]
                if region_name in data_values:
                    self.gdf.at[idx, self.data_column] = data_values[region_name]
            
            print(f"Added data to GeoDataFrame in column '{self.data_column}'")
            return True
        except Exception as e:
            print(f"Error adding data: {e}")
            return False
    
    def generate_random_data(self, data_column_name='random_value', min_val=0, max_val=100):
        """
        Generate random data for demonstration purposes.
        
        Args:
            data_column_name: Name for the data column
            min_val: Minimum value for random data
            max_val: Maximum value for random data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.gdf is None:
            print("GeoDataFrame not loaded.")
            return False
        
        try:
            # Generate random data
            self.data_column = data_column_name
            self.gdf[self.data_column] = np.random.randint(min_val, max_val, size=len(self.gdf))
            
            print(f"Generated random data in column '{self.data_column}'")
            return True
        except Exception as e:
            print(f"Error generating random data: {e}")
            return False
    
    def create_static_choropleth(self, output_path=None, title=None, cmap='viridis'):
        """
        Create a static choropleth map using matplotlib.
        
        Args:
            output_path: Path to save the map image (optional)
            title: Title for the map (optional)
            cmap: Colormap to use
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        if self.gdf is None:
            print("GeoDataFrame not loaded.")
            return None
        
        if self.data_column is None:
            print("No data column specified. Use add_data() or generate_random_data() first.")
            return None
        
        try:
            # Create a choropleth map
            fig, ax = plt.subplots(figsize=(15, 10))
            
            # Plot with colors based on the data column
            self.gdf.plot(
                ax=ax, 
                column=self.data_column, 
                legend=True, 
                cmap=cmap,
                legend_kwds={
                    'label': self.data_column.replace('_', ' ').title(),
                    'orientation': 'horizontal'
                }
            )
            
            # Set title
            if title:
                plt.title(title)
            else:
                plt.title(f"{self.data_column.replace('_', ' ').title()} by Region")
            
            plt.axis('off')  # Hide axes
            plt.tight_layout()
            
            # Save if output path is provided
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                print(f"Choropleth map saved to {output_path}")
            
            return fig
        except Exception as e:
            print(f"Error creating choropleth map: {e}")
            return None
    
    def export_data_as_csv(self, output_path):
        """
        Export the data as a CSV file.
        
        Args:
            output_path: Path to save the CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.gdf is None or self.name_column is None:
            print("GeoDataFrame not properly loaded or name column not identified.")
            return False
        
        try:
            # Create a DataFrame with just the name and data columns
            columns_to_export = [self.name_column]
            if self.data_column:
                columns_to_export.append(self.data_column)
            
            # Add any other columns that might be useful
            for col in self.gdf.columns:
                if col not in columns_to_export and col != 'geometry':
                    columns_to_export.append(col)
            
            # Create the DataFrame and export to CSV
            export_df = self.gdf[columns_to_export].copy()
            export_df.to_csv(output_path, index=False)
            
            print(f"Data exported to {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False 