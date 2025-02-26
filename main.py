from geo_converter import GeoConverter
from choropleth_generator import ChoroplethGenerator
from interactive_map_creator import InteractiveMapCreator
import os

def main():
    """
    Main function to demonstrate the workflow.
    """
    # Step 1: Convert custom JSON to GeoJSON
    converter = GeoConverter()
    
    # Load the custom JSON file
    json_input = "customjson.json"
    geojson_output = "uk_constituencies_local.geojson"
    
    # Load and convert the JSON data
    if converter.load_topojson(json_input):
        converter.save_geojson(geojson_output)
        print(f"Successfully converted custom JSON to GeoJSON")
    else:
        print("Failed to convert custom JSON to GeoJSON.")
    
    geojson_to_use = geojson_output
    
    # Step 2: Generate a choropleth visualization
    choropleth = ChoroplethGenerator()
    
    # Load the GeoJSON
    if choropleth.load_geojson(geojson_to_use):
        # Example data for choropleth (replace with your actual data)
        example_data = {
            # East Sussex constituencies
            "Bexhill and Battle": 75,
            "Crowborough": 42,
            "Tonbridge": 63,
            "Heathfield": 89,
            # Tunbridge Wells constituencies
            "Tunbridge Wells": 58,
            # Add more constituencies if using the complete UK GeoJSON
            "High Weald": 55,
            "Uckfield": 82,
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
    
    # Step 3: Create interactive map
    map_creator = InteractiveMapCreator()
    
    # Load the GeoJSON
    if map_creator.load_geojson(geojson_to_use):
        # Add the same data
        map_creator.add_data(example_data, "example_value")
        
        # Create an interactive map with enhanced features
        map_creator.create_interactive_map(
            output_path="interactive_choropleth.html",
            title="UK Constituencies - Example Values",
            color_scheme="RdYlGn",  # Red-Yellow-Green color scheme
            show_title=True,
            show_legend=True,
            add_layer_control=True,
            zoom_start=6
        )
        
        print("\nInteractive map created successfully!")
        print("Open the HTML file in your web browser to view the map.")
    else:
        print("Failed to load GeoJSON for interactive map creation.")

if __name__ == "__main__":
    main() 