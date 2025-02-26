import folium
import geopandas as gpd
import json
import os
import branca.colormap as cm
import pandas as pd
import numpy as np

class InteractiveMapCreator:
    """
    Class for creating interactive choropleth maps using Folium.
    """
    
    def __init__(self):
        """Initialize the InteractiveMapCreator."""
        self.gdf = None
        self.name_column = None
        self.data_column = None
        self.map = None
    
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
    
    def create_basic_map(self, output_path='interactive_choropleth.html', 
                         tiles='cartodbpositron', zoom_start=9):
        """
        Create a basic interactive choropleth map.
        
        Args:
            output_path: Path to save the HTML map
            tiles: Map tiles to use
            zoom_start: Initial zoom level
            
        Returns:
            folium.Map: The map object
        """
        if self.gdf is None or self.name_column is None:
            print("GeoDataFrame not properly loaded or name column not identified.")
            return None
        
        if self.data_column is None:
            print("No data column specified. Use add_data() or generate_random_data() first.")
            return None
        
        try:
            # Calculate the center of the map
            center_lat = self.gdf.geometry.centroid.y.mean()
            center_lon = self.gdf.geometry.centroid.x.mean()
            
            # Create a Folium map
            self.map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom_start,
                tiles=tiles
            )
            
            # Create a colormap
            min_value = self.gdf[self.data_column].min()
            max_value = self.gdf[self.data_column].max()
            
            colormap = cm.linear.viridis.scale(min_value, max_value)
            colormap.caption = self.data_column.replace('_', ' ').title()
            
            # Convert GeoDataFrame to GeoJSON
            geojson_data = json.loads(self.gdf.to_json())
            
            # Add the choropleth layer
            folium.Choropleth(
                geo_data=geojson_data,
                name='Choropleth',
                data=self.gdf,
                columns=[self.name_column, self.data_column],
                key_on=f'feature.properties.{self.name_column}',
                fill_color='YlGnBu',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name=self.data_column.replace('_', ' ').title()
            ).add_to(self.map)
            
            # Add tooltips
            style_function = lambda x: {'fillColor': '#ffffff', 
                                       'color': '#000000', 
                                       'fillOpacity': 0.1, 
                                       'weight': 0.1}
            highlight_function = lambda x: {'fillColor': '#000000', 
                                           'color': '#000000', 
                                           'fillOpacity': 0.50, 
                                           'weight': 0.1}
            
            # Create tooltip with name and value
            tooltip_fields = [self.name_column, self.data_column]
            tooltip_aliases = ['Constituency:', 'Value:']
            
            # Add GeoJSON layer with tooltips
            folium.GeoJson(
                geojson_data,
                style_function=style_function,
                control=False,
                highlight_function=highlight_function,
                tooltip=folium.features.GeoJsonTooltip(
                    fields=tooltip_fields,
                    aliases=tooltip_aliases,
                    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                )
            ).add_to(self.map)
            
            # Add layer control
            folium.LayerControl().add_to(self.map)
            
            # Add colormap to the map
            self.map.add_child(colormap)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            # Save the map
            self.map.save(output_path)
            print(f"Interactive choropleth map saved to {output_path}")
            
            return self.map
        except Exception as e:
            print(f"Error creating interactive choropleth map: {e}")
            return None
    
    def create_enhanced_map(self, output_path='interactive_choropleth_popup.html', 
                           tiles='cartodbpositron', zoom_start=9):
        """
        Create an enhanced interactive choropleth map with popups.
        
        Args:
            output_path: Path to save the HTML map
            tiles: Map tiles to use
            zoom_start: Initial zoom level
            
        Returns:
            folium.Map: The map object
        """
        if self.gdf is None or self.name_column is None:
            print("GeoDataFrame not properly loaded or name column not identified.")
            return None
        
        if self.data_column is None:
            print("No data column specified. Use add_data() or generate_random_data() first.")
            return None
        
        try:
            # Calculate the center of the map
            center_lat = self.gdf.geometry.centroid.y.mean()
            center_lon = self.gdf.geometry.centroid.x.mean()
            
            # Create a Folium map
            self.map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom_start,
                tiles=tiles
            )
            
            # Create a colormap
            min_value = self.gdf[self.data_column].min()
            max_value = self.gdf[self.data_column].max()
            
            # Function to determine color based on value
            def get_color(value):
                if pd.isna(value):
                    return '#CCCCCC'  # Gray for NaN values
                
                # Create a color scale from red to green
                normalized = (value - min_value) / (max_value - min_value)
                return f'#{int(255 * (1 - normalized)):02x}{int(255 * normalized):02x}00'
            
            # Add the GeoJSON data with custom styling and popups
            for idx, row in self.gdf.iterrows():
                # Get the value for this region
                value = row[self.data_column] if self.data_column in row and not pd.isna(row[self.data_column]) else None
                
                # Create a popup with HTML content
                popup_content = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4>{row[self.name_column]}</h4>
                    <p><strong>Value:</strong> {value if value is not None else 'No data'}</p>
                    <p><strong>ID:</strong> {row.get('id', row.get('ID', 'N/A'))}</p>
                </div>
                """
                
                # Create a GeoJSON feature for this row
                feature = {
                    'type': 'Feature',
                    'geometry': json.loads(row.geometry.to_json()),
                    'properties': {
                        'name': row[self.name_column],
                        'value': value
                    }
                }
                
                # Add the feature to the map with styling
                folium.GeoJson(
                    feature,
                    style_function=lambda x, value=value: {
                        'fillColor': get_color(value),
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.7
                    },
                    popup=folium.Popup(popup_content, max_width=300)
                ).add_to(self.map)
            
            # Add a legend
            legend_html = '''
            <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; 
                        padding: 10px; border: 1px solid grey; border-radius: 5px;">
                <p><strong>''' + self.data_column.replace('_', ' ').title() + '''</strong></p>
                <div style="display: flex; align-items: center;">
                    <div style="background: linear-gradient(to right, #FF0000, #FFFF00, #00FF00); 
                                width: 150px; height: 20px;"></div>
                    <div style="display: flex; justify-content: space-between; width: 150px;">
                        <span>''' + str(min_value) + '''</span>
                        <span>''' + str(max_value) + '''</span>
                    </div>
                </div>
            </div>
            '''
            
            self.map.get_root().html.add_child(folium.Element(legend_html))
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            # Save the map
            self.map.save(output_path)
            print(f"Enhanced interactive choropleth map saved to {output_path}")
            
            return self.map
        except Exception as e:
            print(f"Error creating enhanced interactive choropleth map: {e}")
            return None 