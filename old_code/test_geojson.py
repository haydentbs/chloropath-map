import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import json

def plot_uk_constituencies(output_path=None):
    """
    Plot UK constituencies using GeoJSON data.
    """
    # Use a GeoJSON source instead of TopoJSON
    geojson_url = "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/electoral/eng/westminster/constituencies.geojson"
    
    print(f"Downloading data from {geojson_url}...")
    
    try:
        # Read the GeoJSON directly
        gdf = gpd.read_file(geojson_url)
        print("Successfully loaded GeoJSON data")
        
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
        
        # Create a choropleth map
        fig, ax = plt.subplots(figsize=(12, 10))
        
        if name_column:
            gdf.plot(ax=ax, column=name_column, legend=True, cmap='viridis', 
                     legend_kwds={'loc': 'lower left', 'bbox_to_anchor': (1, 0.5)})
            plt.title(f"UK Constituencies")
        else:
            gdf.plot(ax=ax)
            plt.title("UK Regions (No name column found)")
        
        plt.tight_layout()
        
        # Save if output path is provided
        if output_path:
            plt.savefig(output_path)
            print(f"Map saved to {output_path}")
        
        return fig
    
    except Exception as e:
        print(f"Error: {e}")
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, f"Error loading GeoJSON data:\n{str(e)}", 
                 ha='center', va='center', fontsize=12)
        plt.axis('off')
        
        if output_path:
            plt.savefig(output_path)
        
        return plt.gcf()

# Generate and show the map
fig = plot_uk_constituencies(output_path="uk_constituencies.png")
plt.show() 