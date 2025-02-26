from geo_converter import GeoConverter
from choropleth_generator import ChoroplethGenerator
from interactive_map_creator import InteractiveMapCreator
from data_processing import DataProcessing
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

    # Import the Data ------------------------
    DataObject = DataProcessing('battle_ground.csv')
    client_data = DataObject.process_data()
    
    # Debug: Check client data before adding markers
    print("\nDebug: Client Data Sample:")
    print(client_data[['latitude', 'longitude', 'status']].head())
    print(f"Total clients: {len(client_data)}")
    
    # Create interactive map with both choropleth and markers
    map_creator = InteractiveMapCreator()
    
    # Load the GeoJSON
    if map_creator.load_geojson(geojson_to_use):
        # Calculate average status per constituency using the coordinates
        constituency_scores = map_creator.calculate_point_averages(
            points_df=client_data,
            value_column='status',
            lat_column='latitude',
            lon_column='longitude'
        )
        
        # Add the constituency data
        map_creator.add_data(constituency_scores, "average_status")
        
        # Create the interactive map (but don't save yet)
        map_creator.create_interactive_map(
            title="Estate Agent Relations",
            color_scheme="RdYlGn",
            show_title=True,
            show_legend=True,
            add_layer_control=True,
            zoom_start=10
        )
        
        # Add client markers to the map
        map_creator.add_client_markers(
            client_df=client_data,
            status_column='status',
            lat_column='latitude',
            lon_column='longitude'
        )
        
        # Now save the map with all layers
        map_creator.save_map("interactive_choropleth.html")
        
        print("\nInteractive map created successfully!")
        print("Open the HTML file in your web browser to view the map.")
    else:
        print("Failed to load GeoJSON for interactive map creation.")

if __name__ == "__main__":
    main() 