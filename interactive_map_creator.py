import folium
import geopandas as gpd
import json
import os
import pandas as pd
import numpy as np
from shapely.geometry import mapping
import branca.colormap as cm
from folium.plugins import FloatImage
from shapely.geometry import Point

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
        self.layer_control = None
    
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
    
    def create_interactive_map(self, output_path=None, 
                              title=None, 
                              tiles='cartodbpositron', 
                              zoom_start=7,
                              color_scheme='RdYlGn',
                              show_title=True,
                              show_legend=True,
                              add_layer_control=True):
        """
        Create an interactive choropleth map with popups and layer controls.
        
        Args:
            output_path: Path to save the HTML map (if None, map won't be saved yet)
            title: Title for the map (optional)
            tiles: Map tiles to use (default: 'cartodbpositron')
            zoom_start: Initial zoom level (default: 7)
            color_scheme: Color scheme for choropleth (default: 'RdYlGn')
            show_title: Whether to show the title (default: True)
            show_legend: Whether to show the legend (default: True)
            add_layer_control: Whether to add layer controls (default: True)
            
        Returns:
            folium.Map: The Folium map object
        """
        if self.gdf is None:
            print("GeoDataFrame not loaded.")
            return None
        
        if self.data_column is None:
            print("No data column specified. Use add_data() first.")
            return None
        
        try:
            # Project to Web Mercator for accurate centroid calculation
            gdf_projected = self.gdf.to_crs(epsg=3857)
            
            # Calculate the center of the map
            center_lat = gdf_projected.geometry.centroid.to_crs(epsg=4326).y.mean()
            center_lon = gdf_projected.geometry.centroid.to_crs(epsg=4326).x.mean()
            
            # Create a Folium map
            self.map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom_start,
                tiles=tiles
            )
            
            # Add a title if provided and show_title is True
            if title and show_title:
                title_html = f'''
                <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); 
                            z-index: 1000; background-color: white; padding: 10px; 
                            border: 1px solid grey; border-radius: 5px;">
                    <h3 style="margin: 0;">{title}</h3>
                </div>
                '''
                self.map.get_root().html.add_child(folium.Element(title_html))
            
            # Create a more sophisticated colormap using branca
            min_value = self.gdf[self.data_column].min()
            max_value = self.gdf[self.data_column].max()
            
            # Define color schemes
            color_schemes = {
                'RdYlGn': ['red', 'yellow', 'green'],
                'YlOrRd': ['yellow', 'orange', 'red'],
                'BuPu': ['blue', 'purple'],
                'Spectral': ['red', 'orange', 'yellow', 'green', 'blue'],
                'Blues': ['lightblue', 'darkblue'],
                'Reds': ['lightsalmon', 'darkred'],
                'Greens': ['lightgreen', 'darkgreen'],
                'Purples': ['lavender', 'purple'],
                'Greys': ['lightgrey', 'black']
            }
            
            # Get the colors for the selected scheme or use a default
            colors = color_schemes.get(color_scheme, ['red', 'yellow', 'green'])
            
            # Create a colormap
            colormap = cm.LinearColormap(
                colors=colors,
                vmin=min_value,
                vmax=max_value,
                caption=self.data_column.replace('_', ' ').title()
            )
            
            # Add the colormap to the map if show_legend is True
            if show_legend:
                colormap.add_to(self.map)
            
            # Store feature groups as instance variables so they can be accessed by other methods
            self.base_layer = folium.FeatureGroup(name="Base Map")
            self.choropleth_layer = folium.FeatureGroup(name="Choropleth")
            self.client_layer = folium.FeatureGroup(name="Client Locations")
            
            # Add the GeoJSON data with custom styling and popups
            for idx, row in self.gdf.iterrows():
                # Get the value for this region
                value = row[self.data_column] if self.data_column in row and not pd.isna(row[self.data_column]) else None
                
                # Create a popup with HTML content
                popup_content = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4>{row[self.name_column]}</h4>
                    <p><strong>Value:</strong> {value if value is not None else 'No data'}</p>
                </div>
                """
                
                # Create a GeoJSON feature for this row
                feature = {
                    'type': 'Feature',
                    'geometry': mapping(row.geometry),
                    'properties': {
                        'name': row[self.name_column],
                        'value': value
                    }
                }
                
                # Add base outline to base layer
                folium.GeoJson(
                    feature,
                    style_function=lambda x: {
                        'fillColor': 'transparent',
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0
                    },
                    highlight_function=lambda x: {
                        'fillColor': 'transparent',
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0
                    },
                    tooltip=row[self.name_column],
                    popup=None  # Set popup to None to disable click behavior
                ).add_to(self.base_layer)
                
                # Add colored version to choropleth layer
                if value is not None:
                    # Create a tooltip-only version (no popup)
                    folium.GeoJson(
                        feature,
                        style_function=lambda x, value=value: {
                            'fillColor': colormap(value),
                            'color': 'black',
                            'weight': 1,
                            'fillOpacity': 0.3
                        },
                        highlight_function=lambda x: {
                            'weight': 1,
                            'color': 'black',
                            'fillOpacity': 0.3,
                        },
                        tooltip=f"{row[self.name_column]}: {value}",
                        popup=None  # Set popup to None to disable click behavior
                    ).add_to(self.choropleth_layer)
            
            # Add the layers to the map in specific order
            self.base_layer.add_to(self.map)
            self.choropleth_layer.add_to(self.map)
            self.client_layer.add_to(self.map)
            
            # Add layer control if requested
            if add_layer_control:
                folium.LayerControl().add_to(self.map)
            
            # Add base map options
            folium.TileLayer('openstreetmap', name='OpenStreetMap').add_to(self.map)
            folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(self.map)
            folium.TileLayer('cartodbdark_matter', name='CartoDB Dark Matter').add_to(self.map)
            
            # Add CSS to disable selection highlighting
            css = """
            <style>
            .leaflet-interactive {
                outline: none !important;
            }
            </style>
            """
            self.map.get_root().html.add_child(folium.Element(css))
            
            # # Only save if output_path is provided
            # if output_path:
            #     # Ensure the directory exists
            #     os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
                
            #     # Save the map
            #     self.map.save(output_path)
            #     print(f"Interactive map saved to {output_path}")
            
            return self.map
        except Exception as e:
            print(f"Error creating interactive map: {e}")
            import traceback
            traceback.print_exc()
            return None 

    def add_client_markers(self, client_df, status_column='status', lat_column='latitude', lon_column='longitude'):
        """Add client markers to the map with colors based on their status."""
        if self.map is None:
            print("Map not created yet. Call create_interactive_map first.")
            return
        
        print(f"Adding markers for {len(client_df)} clients...")
        
        if not hasattr(self, 'client_layer'):
            print("Error: client_layer not initialized. Make sure create_interactive_map was called first.")
            return
        
        # Create color mapping for status values (1-8)
        color_map = {
            1: '#ff0000',  # Red
            
            
            2: '#ffbf00',
              # Yellow
            3: '#bfff00',
            
            4: '#00ff00'   # Green
        }
        
        # Add markers for each client
        for _, client in client_df.iterrows():
            try:
                # Get status and coordinates
                status = int(client[status_column])
                lat = float(client[lat_column])
                lon = float(client[lon_column])
                company = str(client['Company'])
                address = str(client['Address'])
                email = str(client['Email'])
                status_str = str(client['status_str'])
                
                # Create popup content
                popup_content = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4>{company}</h4>
                    <p><strong>Status:</strong> {status_str} </p>
                    <p> <strong>Address:</strong> {address} </p>
                    <p> <strong>Email:</strong> {email}</p>
                </div>
                """
                
                # Create a custom icon with the status color
                icon = folium.DivIcon(
                    html=f'''
                        <div style="
                            width: 12px;
                            height: 12px;
                            background-color: {color_map.get(status, '#808080')};
                            border-radius: 50%;
                            border: 1px solid #666;
                        "></div>
                    ''',
                    icon_size=(12, 12),
                    icon_anchor=(6, 6),
                    class_name="custom-pin"
                )
                
                # Create marker with custom icon
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=icon,
                    tooltip=f"Status: {status}"
                ).add_to(self.client_layer)
                
            except Exception as e:
                print(f"Error adding marker: {e}")
                continue
        
        print(f"Successfully added {len(client_df)} markers to the map")

    def save_map(self, output_path):
        """Save the map to an HTML file."""
        if self.map is None:
            print("No map to save. Create a map first.")
            return
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Save the map
        self.map.save(output_path)
        print(f"Interactive map saved to {output_path}")

    def calculate_point_averages(self, points_df, value_column, lat_column='latitude', lon_column='longitude'):
        """
        Calculate average values for points falling within each constituency polygon.
        
        Args:
            points_df (pd.DataFrame): DataFrame containing point data with coordinates
            value_column (str): Name of the column containing values to average
            lat_column (str): Name of the latitude column
            lon_column (str): Name of the longitude column
            
        Returns:
            dict: Dictionary mapping constituency names to average values
        """
        # Convert points DataFrame to GeoDataFrame
        geometry = [Point(xy) for xy in zip(points_df[lon_column], points_df[lat_column])]
        points_gdf = gpd.GeoDataFrame(points_df, geometry=geometry)
        
        # Initialize dictionary to store results
        constituency_averages = {}
        
        # For each constituency polygon
        for idx, constituency in self.gdf.iterrows():
            # Find points that fall within the constituency
            points_within = points_gdf[points_gdf.geometry.within(constituency.geometry)]
            
            if len(points_within) > 0:
                # Calculate average value for points within the constituency
                avg_value = points_within[value_column].mean()
                constituency_averages[constituency[self.name_column]] = avg_value
            else:
                # No points in this constituency
                constituency_averages[constituency[self.name_column]] = None
        
        return constituency_averages 