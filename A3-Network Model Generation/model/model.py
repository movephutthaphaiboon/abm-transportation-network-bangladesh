from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from components import Source, Sink, SourceSink, Bridge, Link, Intersection, Vehicle
import pandas as pd
from collections import defaultdict
import random
import networkx as nx
import csv
import matplotlib.pyplot as plt


# ---------------------------------------------------------------
def set_lat_lon_bound(lat_min, lat_max, lon_min, lon_max, edge_ratio=0.02):
    """
    Set the HTML continuous space canvas bounding box (for visualization)
    give the min and max latitudes and Longitudes in Decimal Degrees (DD)

    Add white borders at edges (default 2%) of the bounding box
    """

    lat_edge = (lat_max - lat_min) * edge_ratio
    lon_edge = (lon_max - lon_min) * edge_ratio

    x_max = lon_max + lon_edge
    y_max = lat_min - lat_edge
    x_min = lon_min - lon_edge
    y_min = lat_max + lat_edge
    return y_min, y_max, x_min, x_max


# ---------------------------------------------------------------
class BangladeshModel(Model):
    """
    The main (top-level) simulation model

    One tick represents one minute; this can be changed
    but the distance calculation need to be adapted accordingly

    Class Attributes:
    -----------------
    step_time: int
        step_time = 1 # 1 step is 1 min

    path_ids_dict: defaultdict
        Key: (origin, destination)
        Value: the shortest path (Infra component IDs) from an origin to a destination

        Only straight paths in the Demo are added into the dict;
        when there is a more complex network layout, the paths need to be managed differently

    sources: list
        all sources in the network

    sinks: list
        all sinks in the network

    """

    step_time = 1

    file_name = '../data/processed/demo_with_intersection.csv'

    def __init__(self, seed=None, x_max=500, y_max=500, x_min=0, y_min=0,  
                 probabilities={}, scenario=0):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []
        self.driving_time = []
        self.driving_distance = []

        self.driving_times = {}
        self.driving_distances = {}

        self.bridge_delays = {}  # {bridge_id: total delay time}
        self.total_wait_time = 0  # initialize total waiting time
        self.probabilities = probabilities # insert probabilities dict
        self.scenario = scenario
        self.condition_list = []
        self.generate_model()
        self.broken_bridges = self.determine_broken_bridges()  # stores broken bridge IDs

    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels
        """

        df = pd.read_csv(self.file_name)

        # a list of names of roads to be generated
        # TODO You can also read in the road column to generate this list automatically
        roads = df.road.unique()

        df_objects_all = []

        # Initialize NetworkX graph
        self.G_nx = nx.Graph()

        for road in roads:
            # Select all the objects on a particular road in the original order as in the cvs
            df_objects_on_road = df[df['road'] == road]

            if not df_objects_on_road.empty:
                df_objects_all.append(df_objects_on_road)

                """
                Set the path 
                1. get the serie of object IDs on a given road in the cvs in the original order
                2. add the (straight) path to the path_ids_dict
                3. put the path in reversed order and reindex
                4. add the path to the path_ids_dict so that the vehicles can drive backwards too
                """
                path_ids = df_objects_on_road['id']
                path_ids.reset_index(inplace=True, drop=True)
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                self.path_ids_dict[path_ids[0], None] = path_ids
                path_ids = path_ids[::-1]
                path_ids.reset_index(inplace=True, drop=True)
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                self.path_ids_dict[path_ids[0], None] = path_ids

                # Add nodes and edges to NetworkX graph
                for _, row in df_objects_on_road.iterrows():
                    self.G_nx.add_node(row['id'], pos=(row['lon'], row['lat']), model_type=row['model_type'])

                for i in range(len(df_objects_on_road) - 1):
                    self.G_nx.add_edge(df_objects_on_road.iloc[i]['id'], df_objects_on_road.iloc[i + 1]['id'],
                                       weight=df_objects_on_road.iloc[i]['length'])
        # print the number of nodes and edges in the graph
        #print("Number of nodes: ", self.G_nx.number_of_nodes())
        #print("Number of edges: ", self.G_nx.number_of_edges())

        # Extract node positions for visualization
        pos = nx.get_node_attributes(self.G_nx, 'pos')

        # Draw the full network
        #plt.figure(figsize=(10, 7))
        #nx.draw(self.G_nx, pos, with_labels=False, node_color='orange', edge_color='gray', node_size=5, font_size=8)
        #plt.show()

        # put back to df with selected roads so that min and max and be easily calculated
        df = pd.concat(df_objects_all)
        y_min, y_max, x_min, x_max = set_lat_lon_bound(
            df['lat'].min(),
            df['lat'].max(),
            df['lon'].min(),
            df['lon'].max(),
            0.05
        )

        # ContinuousSpace from the Mesa package;
        # not to be confused with the SimpleContinuousModule visualization
        self.space = ContinuousSpace(x_max, y_max, True, x_min, y_min)

        for df in df_objects_all:
            for _, row in df.iterrows():  # index, row in ...

                # create agents according to model_type
                model_type = row['model_type'].strip()
                agent = None

                name = row['name']
                if pd.isna(name):
                    name = ""
                else:
                    name = name.strip()

                if model_type == 'source':
                    agent = Source(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                elif model_type == 'sink':
                    agent = Sink(row['id'], self, row['length'], name, row['road'])
                    self.sinks.append(agent.unique_id)
                elif model_type == 'sourcesink':
                    agent = SourceSink(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                    self.sinks.append(agent.unique_id)
                elif model_type == 'bridge':
                    agent = Bridge(row['id'], self, row['condition'], row['length'], row['name'], row['road'])
                elif model_type == 'link':
                    agent = Link(row['id'], self, row['length'], name, row['road'])
                elif model_type == 'intersection':
                    if not row['id'] in self.schedule._agents:
                        agent = Intersection(row['id'], self, row['length'], name, row['road'])

                if agent:
                    self.schedule.add(agent)
                    y = row['lat']
                    x = row['lon']
                    self.space.place_agent(agent, (x, y))
                    agent.pos = (x, y)

    def get_random_route(self, source):
        """
        pick up a random route given an origin
        """
        while True:
            # different source and sink
            sink = self.random.choice(self.sinks)
            #print(source, sink)
            if sink is not source:
                Vehicle.sink = sink
                Vehicle.source = source
                break
        #return self.path_ids_dict[source, sink]
        return self.compute_shortest_path_if_needed(source, sink)
    

    def get_route(self, source):
        """
        Select which routing method to use.
        - 20% chance: Takes a straight route to the end of the road.
        - 80% chance: Picks a random sink.
        - Both cases use shortest path lookup but only compute if not already stored.
        """
        return self.get_random_route(source)  # 80% chance - Random Destination

    def get_straight_route(self, source):
        """
        pick up a straight route given an origin
        """
        return self.compute_shortest_path_if_needed(source, None)

    def compute_shortest_path_if_needed(self, source, sink):
        """
        Compute the shortest path using NetworkX only if it has not been stored yet.
        - Uses `path_ids_dict` if a new shortest path was not computed.
        - Avoids overriding existing paths that may be default ones.
        - Always calculates and stores the shortest path distance.
        """

        # Check if the path already exists in the dictionary
        if (source, sink) in self.path_ids_dict:
            path_ids = self.path_ids_dict[(source, sink)]  # Get existing path

        # Compute shortest path using NetworkX if not already stored
        elif sink and nx.has_path(self.G_nx, source, sink):
            path_ids = nx.shortest_path(self.G_nx, source, sink, weight='weight')
            self.path_ids_dict[(source, sink)] = path_ids  # Store new shortest path
        else:
            return None  # No valid path found

        # Compute and store shortest path distance (even if path was already stored)
        path_distance = nx.shortest_path_length(self.G_nx, source, sink, weight='weight')

        # Ensure only numerical distances are appended
        if isinstance(path_distance, (int, float)):
            self.driving_distance.append(path_distance)
        else:
            print(f"Error: path_distance is not a number! Found {type(path_distance)} instead.")

        #print(f"Path: {path_ids}, Distance: {path_distance}, Source: {source}, Sink: {sink}")

        return path_ids

    def step(self):
        """
        Advance the simulation by one step.
        """
        self.schedule.step()
        #print(f"Step: {self.schedule.steps}")
    
    def determine_broken_bridges(self):
        """
        Determine which bridges are broken at the start of the simulation.
        """
        broken_bridges = set()
        for agent in self.schedule._agents.values():
            if isinstance(agent, Bridge):
                if ((agent.condition == 'A' and random.random() < agent.probabilities[self.scenario]['A']) or 
                    (agent.condition == 'B' and random.random() < agent.probabilities[self.scenario]['B']) or 
                    (agent.condition == 'C' and random.random() < agent.probabilities[self.scenario]['C']) or 
                    (agent.condition == 'D' and random.random() < agent.probabilities[self.scenario]['D'])):
                    broken_bridges.add(agent.unique_id)
                    self.condition_list.append(agent.condition)

        #print(f"Broken bridges for this run: {broken_bridges}"
        return broken_bridges

    def get_average_driving_time(self):
        # Averag driving time of all trucks that reached a Sink (end of the road)
        if not self.driving_time:  # avoid division by zero
            return 0
        return sum(self.driving_time) / len(self.driving_time)

    def get_average_effective_speed(self):
        """
        Compute speed for each truck using stored distances and times.
        Speed is calculated as Distance / Time.
        Returns a list of speeds and the average speed.
        """
        if not self.driving_times or not self.driving_distances:
            return 0  # No valid data

        # Compute speed for each truck (avoid division by zero)
        speeds = [
            self.driving_distances[truck_id] / self.driving_times[truck_id]
            for truck_id in self.driving_times
            if self.driving_times[truck_id] > 0
        ]

        # Compute average speed
        avg_speed = sum(speeds) / len(speeds) if speeds else 0

        #print(f"Speeds: {speeds}")
        #print(f"Average Speed: {avg_speed}")

        return avg_speed


    def get_biggest_bridge_delay(self):
        '''
        Return the 10 bridges with the biggest total delay time in a dictionary form.
            key=name of the bridge
            value=total accumulated delay time of the bridge
        If there is no bridge with delay then return a tuple
        with the first element being None (name of the bridge) and the second element being 0
        (caused delay time by that bridge).
        '''
        if not self.bridge_delays:
            return None, 0  # No bridge delays recorded
        
        top_10 = dict(sorted(self.bridge_delays.items(), key=lambda item: item[1], reverse=True)[:10])
        return top_10


    def get_total_delay_time(self):
        '''
        Return the total waiting time of all trucks that reached a Sink (end of the road).
        '''
        return self.total_wait_time
    

    def get_average_delay_time(self):
        '''
        Return the average waiting time of all trucks that reached a Sink (end of the road).
        If no trucks reached a Sink, return 0.

        We calculate the average waiting time by dividing the total waiting time
        by the number of trucks that reached a Sink.
        '''
        total_trucks = len(self.driving_time)  # total trucks that reached a Sink
        if total_trucks == 0:
            return 0  # avoid division by zero
        return self.total_wait_time / total_trucks
    

    def get_broken_bridges(self):
        '''
        Return the list of broken bridges
        '''
        return list(self.broken_bridges)
    
    
    def collect_data(self):
        """
        Collect data from the vehicles at each step.
        """
        for agent in self.schedule.agents:
            if isinstance(agent, Vehicle):
                self.data.append({
                    'step': self.schedule.steps,
                    'model type': agent.__class__.__name__,
                    'id': agent.unique_id,
                    'location': agent.location.unique_id,
                    'location_offset': agent.location_offset,
                    'state': agent.state.name,
                    'waiting_time': agent.waiting_time,
                    'generated_at_step': agent.generated_at_step,
                    'removed_at_step': agent.removed_at_step,})
                
                
    def save_data(self, filename='scenario_non_numbered.csv'): #modified
        """
        Save collected data from the vehicles to a CSV file.
        """
        keys = self.data[0].keys()
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys, delimiter =';') #modified
            dict_writer.writeheader()
            dict_writer.writerows(self.data)

# EOF -----------------------------------------------------------
