from geo_converter import GeoConverter
from choropleth_generator import ChoroplethGenerator
from interactive_map_creator import InteractiveMapCreator
import os

def main():
    """
    Main function to demonstrate the workflow.
    """
    # Step 1: Convert TopoJSON to GeoJSON or download complete UK GeoJSON
    converter = GeoConverter()
    
    # Option 1: Convert multiple TopoJSON URLs to a single GeoJSON
    topojson_urls = [
        "https://martinjc.github.io/UK-GeoJSON/json/eng/wpc_by_lad/topo_E07000065.json",  # East Sussex
        "https://martinjc.github.io/UK-GeoJSON/json/eng/wpc_by_lad/topo_E07000116.json"   # Tunbridge Wells
    ]
    geojson_output = "uk_constituencies_local.geojson"
    
    # Load and merge the TopoJSON data
    if converter.load_topojson(topojson_urls):
        converter.save_geojson(geojson_output)
        print(f"Successfully created merged GeoJSON from {len(topojson_urls)} sources")
    else:
        print("Failed to convert TopoJSON to GeoJSON.")
    
    # Option 2: Download a complete UK constituencies GeoJSON
    # This is more reliable for creating proper choropleth maps
    complete_geojson_output = "uk_constituencies_complete.geojson"
    converter.download_complete_uk_geojson(complete_geojson_output)
    
    # Use the complete GeoJSON for the rest of the workflow
    geojson_to_use = complete_geojson_output if os.path.exists(complete_geojson_output) else geojson_output
    
    # Step 2: Generate a choropleth visualization
    choropleth = ChoroplethGenerator()
    
    # Load the GeoJSON
    if choropleth.load_geojson(geojson_to_use):
        # Example data for choropleth (replace with your actual data)
        example_data = {
            # East Sussex constituencies
            "Bexhill and Battle": 75,
            "Eastbourne": 42,
            "Lewes": 63,
            "Wealden": 89,
            # Tunbridge Wells constituencies
            "Tunbridge Wells": 58,
            # Add more constituencies if using the complete UK GeoJSON
            "Brighton, Kemptown": 55,
            "Brighton, Pavilion": 82,
            "Hove": 67
        }
        
        # Add the data to the GeoDataFrame
        choropleth.add_data(example_data, "example_value")
        
        # Create a static choropleth map
        choropleth.create_static_choropleth(
            output_path="static_choropleth.png",
            title="Example Values by Constituency"
        )
        
        # Export the data as CSV
        choropleth.export_data_as_csv("constituency_data.csv")
    else:
        print("Failed to load GeoJSON for choropleth generation.")
        return
    
    # Step 3: Create interactive maps
    map_creator = InteractiveMapCreator()
    
    # Load the GeoJSON
    if map_creator.load_geojson(geojson_to_use):
        # Add the same data
        map_creator.add_data(example_data, "example_value")
        
        # Create a basic interactive map
        map_creator.create_basic_map(
            output_path="interactive_choropleth.html"
        )
        
        # Create an enhanced interactive map with popups
        map_creator.create_enhanced_map(
            output_path="interactive_choropleth_popup.html"
        )
        
        print("\nAll maps created successfully!")
        print("Open the HTML files in your web browser to view the interactive maps.")
    else:
        print("Failed to load GeoJSON for interactive map creation.")

if __name__ == "__main__":
    main() 