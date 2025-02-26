import folium
import geopandas as gpd
import os
import random
import numpy as np
import requests
import json
import topojson as tp

def generate_choropleth_map(geojson_url, output_path='templates/client_map.html'):
    """
    Generate a choropleth map using the provided GeoJSON/TopoJSON data.
    
    Args:
        geojson_url: URL to the GeoJSON/TopoJSON data
        output_path: Path to save the HTML map
    """
    print(f"Downloading data from {geojson_url}...")
    
    # Instead of trying to convert TopoJSON to GeoJSON in Python,
    # let's use geopandas to read directly from the URL
    try:
        # First attempt: Try to read directly from the URL
        gdf = gpd.read_file(geojson_url)
        print("Successfully loaded data directly from URL")
    except Exception as e:
        print(f"Error reading directly from URL: {e}")
        
        # Second attempt: Download the data and save it locally, then read
        response = requests.get(geojson_url)
        data = response.json()
        
        # Save to a temporary file
        temp_file = "temp_geojson.json"
        with open(temp_file, 'w') as f:
            json.dump(data, f)
        
        try:
            # Try to read the saved file
            gdf = gpd.read_file(temp_file)
            print("Successfully loaded data from temporary file")
        except Exception as e2:
            print(f"Error reading from temporary file: {e2}")
            
            # If all else fails, try to extract features manually
            print("Attempting manual extraction...")
            features = []
            
            # Check if it's TopoJSON format
            if "objects" in data and "transform" in data:
                object_key = list(data["objects"].keys())[0]
                
                # For TopoJSON, we'll need to use a different approach
                # Let's try to use an online converter
                print("Detected TopoJSON format. Using online converter...")
                
                # Save the TopoJSON to a temporary file
                with open("temp_topo.json", 'w') as f:
                    json.dump(data, f)
                
                # Use mapshaper CLI if available, otherwise suggest installation
                try:
                    import subprocess
                    result = subprocess.run(
                        ["mapshaper", "-i", "temp_topo.json", "-o", "temp_geo.json", "format=geojson"],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        gdf = gpd.read_file("temp_geo.json")
                        print("Successfully converted using mapshaper")
                    else:
                        print(f"Mapshaper error: {result.stderr}")
                        raise Exception("Mapshaper conversion failed")
                except Exception as e3:
                    print(f"Error using mapshaper: {e3}")
                    print("\nPlease install Node.js and mapshaper:")
                    print("1. Install Node.js from https://nodejs.org/")
                    print("2. Run: npm install -g mapshaper")
                    print("3. Try running this script again")
                    
                    # As a last resort, try to use a different URL
                    print("\nAttempting to use a different GeoJSON source...")
                    alternative_url = "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/electoral/eng/westminster/constituencies.geojson"
                    try:
                        gdf = gpd.read_file(alternative_url)
                        print(f"Successfully loaded data from alternative source: {alternative_url}")
                    except Exception as e4:
                        print(f"Error loading alternative source: {e4}")
                        raise Exception("Could not load any geographic data")
    
    # Print available columns to help with debugging
    print(f"Available columns: {gdf.columns.tolist()}")
    
    # Find appropriate name and code columns
    name_column = None
    code_column = None
    
    # Look for name column
    name_candidates = ['PCON13NM', 'name', 'NAME', 'constituency_name', 'CONSTITUENCY_NAME']
    for col in name_candidates:
        if col in gdf.columns:
            name_column = col
            break
    
    # If no name column found, look for columns with 'name' or 'nm' in them
    if name_column is None:
        name_cols = [col for col in gdf.columns if 'name' in col.lower() or 'nm' in col.lower()]
        if name_cols:
            name_column = name_cols[0]
        else:
            # Use the first string column as a fallback
            for col in gdf.columns:
                if gdf[col].dtype == 'object' and col != 'geometry':
                    name_column = col
                    break
            
            # If still no column found, use the first non-geometry column
            if name_column is None:
                non_geom_cols = [col for col in gdf.columns if col != 'geometry']
                if non_geom_cols:
                    name_column = non_geom_cols[0]
                else:
                    # Create a dummy column if nothing else works
                    gdf['area_id'] = range(1, len(gdf) + 1)
                    name_column = 'area_id'
    
    # Look for code column
    code_candidates = ['PCON13CD', 'code', 'CODE', 'id', 'ID', 'constituency_code']
    for col in code_candidates:
        if col in gdf.columns:
            code_column = col
            break
    
    # If no code column found, use the name column
    if code_column is None:
        code_column = name_column
    
    print(f"Using '{name_column}' as name column and '{code_column}' as code column")
    
    # Create a base map centered on the data
    if not gdf.empty:
        center_lat = gdf.geometry.centroid.y.mean()
        center_lon = gdf.geometry.centroid.x.mean()
    else:
        # Default to UK coordinates if GeoDataFrame is empty
        center_lat = 54.0
        center_lon = -2.0
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles='cartodbpositron'  # Light map style
    )
    
    # Generate random colors for each area
    def random_color():
        return f'#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}'
    
    # Create a dictionary mapping area names to random colors
    colors = {str(name): random_color() for name in gdf[name_column].unique()}
    
    # Add GeoJSON layer with tooltips for interactivity
    folium.GeoJson(
        gdf,
        name='Area Details',
        style_function=lambda feature: {
            'fillColor': colors.get(str(feature['properties'][name_column]), '#FFFF00'),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[name_column, code_column],
            aliases=['Area:', 'Code:'],
            localize=True
        )
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    m.save(output_path)
    
    print(f"Map generated and saved to {output_path}")
    
    # Clean up temporary files
    for temp_file in ['temp_geojson.json', 'temp_topo.json', 'temp_geo.json']:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
    
    return m

def create_interactive_map(output_path='templates/client_map.html'):
    """
    Create an interactive map using Folium with GeoJSON data.
    
    Args:
        output_path: Path to save the HTML map
    """
    # Use a GeoJSON source instead of TopoJSON
    geojson_url = "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/electoral/eng/westminster/constituencies.geojson"
    
    print(f"Downloading data from {geojson_url}...")
    
    try:
        # Create a Folium map centered on the UK
        m = folium.Map(location=[54.0, -2.0], zoom_start=6)
        
        # Try to load the GeoJSON directly with GeoPandas
        gdf = gpd.read_file(geojson_url)
        
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
        
        # Convert to GeoJSON for Folium
        geojson_data = json.loads(gdf.to_json())
        
        # Add the GeoJSON to the map
        folium.GeoJson(
            geojson_data,
            name='UK Constituencies',
            style_function=lambda feature: {
                'fillColor': '#3388ff',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.5,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[name_column] if name_column else [],
                aliases=['Constituency:'] if name_column else [],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
            )
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        # Create a simple map with an error message
        m = folium.Map(location=[54.0, -2.0], zoom_start=6)
        folium.Marker(
            [54.0, -2.0],
            popup=f"Error loading GeoJSON data: {str(e)}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the map
    m.save(output_path)
    print(f"Interactive map saved to {output_path}")
    
    return m

if __name__ == "__main__":
    # Create the interactive map
    map = create_interactive_map() 