import geopandas as gpd
import json
import requests
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, shape
import os
import random

def generate_choropleth_map(topojson_url, output_path=None, geojson_output=None, data_column=None, data_values=None):
    """
    Generate a visualization using TopoJSON data and optionally save the GeoJSON for future use.
    
    Args:
        topojson_url: URL to the TopoJSON data
        output_path: Path to save the visualization (optional)
        geojson_output: Path to save the extracted GeoJSON (optional)
        data_column: Column name to use for choropleth coloring (optional)
        data_values: Dictionary mapping region names to values for choropleth (optional)
    """
    print(f"Downloading data from {topojson_url}...")
    
    # Download the TopoJSON data
    response = requests.get(topojson_url)
    topology = json.loads(response.text)
    
    # First, identify the object name (in this case 'E07000065')
    object_name = list(topology['objects'].keys())[0]
    
    # Try to read directly with GeoPandas
    try:
        print("Attempting to read TopoJSON directly with GeoPandas...")
        gdf = gpd.read_file(topojson_url)
        print("Successfully loaded data with GeoPandas")
        
        # If we have data_values, add them to the GeoDataFrame
        if data_column and data_values:
            # Create the data column if it doesn't exist
            if data_column not in gdf.columns:
                gdf[data_column] = np.nan
            
            # Fill in values from the data_values dictionary
            for idx, row in gdf.iterrows():
                region_name = row['PCON13NM']
                if region_name in data_values:
                    gdf.at[idx, data_column] = data_values[region_name]
        
        # Save GeoJSON if requested
        if geojson_output:
            # Ensure directory exists
            os.makedirs(os.path.dirname(geojson_output) if os.path.dirname(geojson_output) else '.', exist_ok=True)
            gdf.to_file(geojson_output, driver='GeoJSON')
            print(f"GeoJSON saved to {geojson_output}")
        
        # Create a choropleth map
        plt.figure(figsize=(12, 8))
        ax = plt.axes()
        
        # Use the data column if provided, otherwise use PCON13NM
        column_to_plot = data_column if data_column and data_column in gdf.columns else 'PCON13NM'
        
        # Plot with colors based on the selected column
        gdf.plot(ax=ax, column=column_to_plot, legend=True, cmap='viridis')
        
        plt.title(f"UK Regions - {object_name}")
        plt.tight_layout()
        
    except Exception as e:
        print(f"Error reading with GeoPandas: {e}")
        
        # Create a GeoDataFrame with just the properties
        properties_list = []
        for geometry in topology['objects'][object_name]['geometries']:
            if 'properties' in geometry:
                properties_list.append(geometry['properties'])
        
        # Create a DataFrame (not GeoDataFrame) for visualization
        import pandas as pd
        df = pd.DataFrame(properties_list)
        
        # Create a bar chart of constituency names
        plt.figure(figsize=(12, 8))
        if 'PCON13NM' in df.columns:
            # If we have data_values, create a new column with those values
            if data_column and data_values:
                df[data_column] = df['PCON13NM'].map(data_values)
                
                # Plot the data values if available
                if data_column in df.columns and not df[data_column].isna().all():
                    df.sort_values(data_column, ascending=False).plot(
                        kind='bar', x='PCON13NM', y=data_column, figsize=(14, 8)
                    )
                    plt.title(f"{data_column} by Constituency")
                    plt.xlabel("Constituency")
                    plt.ylabel(data_column)
                else:
                    df['PCON13NM'].value_counts().plot(kind='bar')
                    plt.title(f"UK Constituencies in {object_name}")
                    plt.xlabel("Constituency")
                    plt.ylabel("Count")
            else:
                df['PCON13NM'].value_counts().plot(kind='bar')
                plt.title(f"UK Constituencies in {object_name}")
                plt.xlabel("Constituency")
                plt.ylabel("Count")
                
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
        else:
            print("No PCON13NM column found in the data")
            # Create a simple text visualization of available columns
            plt.text(0.5, 0.5, f"Available columns: {', '.join(df.columns)}", 
                     ha='center', va='center', fontsize=12)
            plt.title("TopoJSON Data Structure")
            plt.axis('off')
    
    # Save if output path is provided
    if output_path:
        plt.savefig(output_path)
        print(f"Visualization saved to {output_path}")
    
    return plt.gcf()

def create_country_wide_choropleth(geojson_path=None, data_values=None, output_path=None):
    """
    Create a country-wide choropleth map using saved GeoJSON data.
    
    Args:
        geojson_path: Path to the GeoJSON file
        data_values: Dictionary mapping region names to values for choropleth
        output_path: Path to save the visualization
    """
    if not geojson_path:
        # Use a GeoJSON source for all UK constituencies
        geojson_path = "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/electoral/eng/westminster/constituencies.geojson"
    
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
        
        # Create a choropleth map
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # Plot with colors based on the data column
        gdf.plot(ax=ax, column=data_column, legend=True, cmap='viridis',
                 legend_kwds={'label': data_column.replace('_', ' ').title(),
                              'orientation': 'horizontal'})
        
        plt.title(f"UK Constituencies - {data_column.replace('_', ' ').title()}")
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

# Example usage:
if __name__ == "__main__":
    # URL to the TopoJSON data
    topojson_url = "https://martinjc.github.io/UK-GeoJSON/json/eng/wpc_by_lad/topo_E07000065.json"
    
    # Save the GeoJSON for future use
    geojson_output = "uk_constituencies.geojson"
    
    # Example data for choropleth (replace with your actual data)
    # This could be election results, demographic data, etc.
    example_data = {
        "Bexhill and Battle": 75,
        "Eastbourne": 42,
        "Lewes": 63,
        "Wealden": 89
    }
    
    # Generate the visualization and save the GeoJSON
    fig1 = generate_choropleth_map(
        topojson_url, 
        output_path="uk_regions_viz.png",
        geojson_output=geojson_output,
        data_column="example_value",
        data_values=example_data
    )
    
    # Create a country-wide choropleth map
    # This uses the saved GeoJSON or falls back to a URL
    fig2 = create_country_wide_choropleth(
        geojson_path=geojson_output if os.path.exists(geojson_output) else None,
        data_values=example_data,
        output_path="uk_country_choropleth.png"
    )
    
    # Show the visualizations
    plt.show()

