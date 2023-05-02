# Route Planner with Speed Limit and Stop Location

This script is a route planner that finds a suitable stop location between a start and end address based on the maximum range of an EV and an average speed limit close to 55 mph. It reads a CSV file containing potential charger locations and calculates the route using Google Maps API.

## Dependencies

You can install the dependencies using pip:

- googlemaps
- gmplot
- pandas
- folium
- bs4


To run the script, open a terminal and navigate to the directory where the script is located. Then, run the following command:

python script.py <start_address> <end_address> <max_distance_miles> <csv_file_path>

- `<start_address>`: The starting address (e.g., "123 Main St, Anytown, USA").
- `<end_address>`: The ending address (e.g., "789 Elm St, Othertown, USA").
- `<max_distance_miles>`: The maximum distance (in miles) the vehicle can travel before needing to stop.
- `<csv_file_path>`: The path to the CSV file containing potential stop locations.

