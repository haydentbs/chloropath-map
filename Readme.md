# Interactive Map Creation

This project demonstrates the workflow for creating an interactive map using custom JSON data, client data, and GeoJSON files. The map includes a choropleth layer and client markers, providing a visual representation of data across different regions.

## Overview

The `main.py` script is the main entry point for this project. It performs the following tasks:

1. Converts a custom JSON file to a GeoJSON format.
2. Processes client data from a CSV file.
3. Creates an interactive map with a choropleth layer and client markers.
4. Saves the map as an HTML file for viewing in a web browser.

## Prerequisites

- Python 3.x
- Required Python packages: `geopandas`, `folium`, `pandas`, `numpy`, `shapely`, `branca`

## Usage

1. **Convert JSON to GeoJSON**: The script uses the `GeoConverter` class to convert a custom JSON file (`customjson.json`) to a GeoJSON file (`uk_constituencies_local.geojson`).

2. **Process Client Data**: The `DataProcessing` class processes client data from `battle_ground.csv`, extracting relevant information for mapping.

3. **Create Interactive Map**: The `InteractiveMapCreator` class is used to:
   - Load the GeoJSON data.
   - Calculate average status per constituency.
   - Add data to the map.
   - Add client markers.
   - Save the map as `interactive_choropleth.html`.

4. **View the Map**: Open the `interactive_choropleth.html` file in a web browser to view the interactive map.

## Code Structure

- **GeoConverter**: Handles conversion of custom JSON to GeoJSON.
- **DataProcessing**: Processes client data from CSV.
- **InteractiveMapCreator**: Manages the creation and customization of the interactive map.

## Example

To run the script, execute the following command in your terminal:

`
bash
python main.py
`

## Screenshot

![Interactive Map Screenshot](path/to/screenshot.png)

## Troubleshooting

- Ensure all required Python packages are installed.
- Verify the paths to input files (`customjson.json`, `battle_ground.csv`) are correct.

## References

- `main.py` script: 
  ```python:main.py
  startLine: 1
  endLine: 79
  ```

- `InteractiveMapCreator` class:
  ```python:interactive_map_creator.py
  startLine: 12
  endLine: 416
  ```

## License

This project is licensed under the MIT License.
