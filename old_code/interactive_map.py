import folium
import geopandas as gpd
import json
import os
import branca.colormap as cm
import pandas as pd
import numpy as np

def create_interactive_choropleth(geojson_path, data_values=None, output_path='interactive_choropleth.html'):
    """
    Create an interactive choropleth map using Folium with the saved GeoJSON data.
    
    Args:
        geojson_path: Path to the GeoJSON file
        data_values: Dictionary mapping region names to values for choropleth
        output_path: Path to save the HTML map
    """
    print(f"Loading GeoJSON from {geojson_path}...")
    
    try:
        # Read the GeoJSON
        gdf = gpd.read_file(geojson_path)
        print(f"Successfully loaded GeoJSON with {len(gdf)} regions")
        
        # Find the name column
        name_column = None
        for col in ['PCON13NM', 'name', 'NAME', 'constituency_name']:
            if col in gdf.columns:
                name_column = col
                break
        
        if name_column is None:
            # Look for columns with 'name' in them
            name_cols = [col for col in gdf.columns if 'name' in col.lower()]
            if name_cols:
                name_column = name_cols[0]
        
        if not name_column:
            print("Could not find a name column in the GeoJSON")
            return None
        
        # If we have data_values, add them to the GeoDataFrame
        if data_values:
            # Create a data column
            data_column = 'choropleth_value'
            gdf[data_column] = np.nan
            
            # Fill in values from the data_values dictionary
            for idx, row in gdf.iterrows():
                region_name = row[name_column]
                if region_name in data_values:
                    gdf.at[idx, data_column] = data_values[region_name]
        else:
            # Generate random data for demonstration
            data_column = 'random_value'
            gdf[data_column] = np.random.randint(1, 100, size=len(gdf))
        
        # Calculate the center of the map
        center_lat = gdf.geometry.centroid.y.mean()
        center_lon = gdf.geometry.centroid.x.mean()
        
        # Create a Folium map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=9,
            tiles='cartodbpositron'  # Light map style
        )
        
        # Create a colormap
        min_value = gdf[data_column].min()
        max_value = gdf[data_column].max()
        
        colormap = cm.linear.viridis.scale(min_value, max_value)
        colormap.caption = data_column.replace('_', ' ').title()
        
        # Convert GeoDataFrame to GeoJSON
        geojson_data = json.loads(gdf.to_json())
        
        # Add the choropleth layer
        folium.Choropleth(
            geo_data=geojson_data,
            name='Choropleth',
            data=gdf,
            columns=[name_column, data_column],
            key_on=f'feature.properties.{name_column}',
            fill_color='YlGnBu',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=data_column.replace('_', ' ').title()
        ).add_to(m)
        
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
        tooltip_fields = [name_column, data_column]
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
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add colormap to the map
        m.add_child(colormap)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Save the map
        m.save(output_path)
        print(f"Interactive choropleth map saved to {output_path}")
        
        return m
    
    except Exception as e:
        print(f"Error creating interactive choropleth map: {e}")
        return None

def create_interactive_choropleth_with_popup(geojson_path, data_values=None, output_path='interactive_choropleth_popup.html'):
    """
    Create an interactive choropleth map with popups showing additional information.
    
    Args:
        geojson_path: Path to the GeoJSON file
        data_values: Dictionary mapping region names to values for choropleth
        output_path: Path to save the HTML map
    """
    print(f"Loading GeoJSON from {geojson_path}...")
    
    try:
        # Read the GeoJSON
        gdf = gpd.read_file(geojson_path)
        print(f"Successfully loaded GeoJSON with {len(gdf)} regions")
        
        # Find the name column
        name_column = None
        for col in ['PCON13NM', 'name', 'NAME', 'constituency_name']:
            if col in gdf.columns:
                name_column = col
                break
        
        if name_column is None:
            # Look for columns with 'name' in them
            name_cols = [col for col in gdf.columns if 'name' in col.lower()]
            if name_cols:
                name_column = name_cols[0]
        
        if not name_column:
            print("Could not find a name column in the GeoJSON")
            return None
        
        # If we have data_values, add them to the GeoDataFrame
        if data_values:
            # Create a data column
            data_column = 'choropleth_value'
            gdf[data_column] = np.nan
            
            # Fill in values from the data_values dictionary
            for idx, row in gdf.iterrows():
                region_name = row[name_column]
                if region_name in data_values:
                    gdf.at[idx, data_column] = data_values[region_name]
        else:
            # Generate random data for demonstration
            data_column = 'random_value'
            gdf[data_column] = np.random.randint(1, 100, size=len(gdf))
        
        # Calculate the center of the map
        center_lat = gdf.geometry.centroid.y.mean()
        center_lon = gdf.geometry.centroid.x.mean()
        
        # Create a Folium map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=9,
            tiles='cartodbpositron'
        )
        
        # Create a colormap
        min_value = gdf[data_column].min()
        max_value = gdf[data_column].max()
        
        # Function to determine color based on value
        def get_color(value):
            if pd.isna(value):
                return '#CCCCCC'  # Gray for NaN values
            
            # Create a color scale from red to green
            normalized = (value - min_value) / (max_value - min_value)
            return f'#{int(255 * (1 - normalized)):02x}{int(255 * normalized):02x}00'
        
        # Add the GeoJSON data with custom styling and popups
        for idx, row in gdf.iterrows():
            # Get the value for this region
            value = row[data_column] if data_column in row and not pd.isna(row[data_column]) else None
            
            # Create a popup with HTML content
            popup_content = f"""
            <div style="font-family: Arial; width: 200px;">
                <h4>{row[name_column]}</h4>
                <p><strong>Value:</strong> {value if value is not None else 'No data'}</p>
                <p><strong>ID:</strong> {row.get('id', row.get('ID', 'N/A'))}</p>
            </div>
            """
            
            # Create a GeoJSON feature for this row
            feature = {
                'type': 'Feature',
                'geometry': json.loads(row.geometry.to_json()),
                'properties': {
                    'name': row[name_column],
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
            ).add_to(m)
        
        # Add a legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; 
                    padding: 10px; border: 1px solid grey; border-radius: 5px;">
            <p><strong>''' + data_column.replace('_', ' ').title() + '''</strong></p>
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
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Save the map
        m.save(output_path)
        print(f"Interactive choropleth map with popups saved to {output_path}")
        
        return m
    
    except Exception as e:
        print(f"Error creating interactive choropleth map with popups: {e}")
        return None

if __name__ == "__main__":
    # Path to the GeoJSON file
    geojson_path = "uk_constituencies.geojson"
    
    # Example data for choropleth (replace with your actual data)
    example_data = {
        "Bexhill and Battle": 75,
        "Eastbourne": 42,
        "Lewes": 63,
        "Wealden": 89
    }
    
    # Create a basic interactive choropleth map
    map1 = create_interactive_choropleth(
        geojson_path=geojson_path,
        data_values=example_data,
        output_path="interactive_choropleth.html"
    )
    
    # Create an enhanced interactive choropleth map with popups
    map2 = create_interactive_choropleth_with_popup(
        geojson_path=geojson_path,
        data_values=example_data,
        output_path="interactive_choropleth_popup.html"
    )
    
    print("\nInteractive maps created successfully!")
    print("Open the HTML files in your web browser to view the maps.") 