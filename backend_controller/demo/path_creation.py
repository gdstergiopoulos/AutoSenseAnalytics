import osmnx as ox
import networkx as nx
import folium
import random
from shapely.geometry import LineString, Point
import time 

# 1. Download the road network for a city
city = "London, UK"

# graph = ox.graph_from_place(city, network_type="drive")
graph= ox.graph_from_bbox((21.730227,38.242933,21.742630,38.251881),network_type='drive')


# 2. Generate random starting points (nodes) for cars
num_cars = 4
nodes = list(graph.nodes)
car_positions = random.sample(nodes, num_cars)

# 3. Simulate movement of cars
def simulate_movements(graph, car_positions, steps=20):
    movements = {car: [] for car in car_positions}

    for step in range(steps):
        for car in car_positions:
            # Get current position
            current_node = car_positions[car]
            movements[car].append(graph.nodes[current_node])

            # Move to a random neighboring node
            neighbors = list(graph.neighbors(current_node))
            if neighbors:
                car_positions[car] = random.choice(neighbors)

    return movements

# Initialize car positions and simulate
car_positions = {car: random.choice(nodes) for car in range(num_cars)}
movements = simulate_movements(graph, car_positions)

# Correct map center calculation
nodes, edges = ox.graph_to_gdfs(graph, nodes=True, edges=True)
map_center = (nodes.geometry.y.mean(), nodes.geometry.x.mean())

# Create a Folium map
city_map = folium.Map(location=map_center, zoom_start=13)

# Add the road network
for _, row in edges.iterrows():
    line = LineString(row.geometry)
    folium.PolyLine([(coord[1], coord[0]) for coord in line.coords], color="gray", weight=1).add_to(city_map)

# for _, row in edges.sample(frac=0.1).iterrows():  # Use 10% of edges
#     line = LineString(row.geometry)
#     folium.PolyLine([(coord[1], coord[0]) for coord in line.coords], color="gray", weight=1).add_to(city_map)



# Add cars and their movements
colors = ["red", "blue", "green", "orange", "purple", "black", "yellow", "brown", "pink", "cyan"]
list_of_paths=[]
for car, path in movements.items():
    path_coords = [(node['y'], node['x']) for node in path]
    print(path_coords)
    # list_of_paths.append(path_coords)
    list_of_paths.append([{"car":car,"path":[{"lat":coord[0],"lon":coord[1]} for coord in path_coords]}])
    folium.PolyLine(path_coords, color=random.choice(colors), weight=2.5).add_to(city_map)

import json 
with open('path.json', 'w') as f:
    json.dump({"paths": list_of_paths},f,indent=4)    

import flask
from flask_cors import CORS 
app = flask.Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return flask.send_file('car_simulation.html')


@app.route('/path')
def path():
    return flask.send_file('./path.json')

@app.route('/path/<int:car>')
def path_car(car):
    return flask.jsonify(list_of_paths[car])

app.run()
# for carpath in list_of_paths:
#     color=random.choice(colors)
#     for coord in carpath:
#         folium.Marker(location=[coord[0], coord[1]], icon=folium.Icon(color=color)).add_to(city_map)
#         #add delay
#         time.sleep(0.3)
#         #remove marker



# Save the map as HTML
city_map.save("./car_simulation.html")

print("Simulation complete! Open 'car_simulation.html' to view the map.")


