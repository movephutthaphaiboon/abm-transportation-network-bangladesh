from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from components import Source, Sink, SourceSink, Bridge, Link, Intersection
import pandas as pd
from collections import defaultdict
import networkx as nx
import random
import heapq

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

    # file_name = '../data/demo-4.csv'
    file_name = '../data/processed/demo_100_complete.csv'

    def __init__(self, seed=None, x_max=500, y_max=500, x_min=0, y_min=0,
                 probabilities={}, scenario=0, 
                 flood=False, heavy_truck = False
                 ):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []
        self.G = nx.Graph()

        self.driving_time = []
        self.bridge_delays = {}  # {bridge_id: total delay time}
        self.total_wait_time = 0  # initialize total waiting time
        self.probabilities = probabilities # insert probabilities dict
        self.scenario = scenario 
        self.condition_list = []
        self.flood = flood
        self.heavy_truck = heavy_truck

        self.generate_model()
        self.broken_bridges = self.determine_broken_bridges()

    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels
        """

        df = pd.read_csv(self.file_name)

        # a list of names of roads to be generated
        # TODO You can also read in the road column to generate this list automatically
        # roads = ['N1', 'N2']

        roads = df['road'].unique()

        # roads = df['road'].unique()

        df_objects_all = []
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

                """
                Create NetworkX Graph road by road (path by path)
                """
                path_G = nx.path_graph(path_ids)
                self.G.add_nodes_from(path_G)
                self.G.add_edges_from(path_G.edges)

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
                    agent = SourceSink(row['id'], self, row['length'], name, row['road'], 
                                       selection_probability=row['sink_selection_probability'], 
                                       generation_frequency=row['truck_generation_frequency']) ###
                    self.sources.append(agent.unique_id)
                    self.sinks.append(agent.unique_id)
                elif model_type == 'bridge':
                    agent = Bridge(row['id'], self, row['length'], name, row['road'], row['condition'], 
                                   row['FLOODCAT'], row['heavy_truck_normalized'])
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

    def get_straight_route(self, source):
        return self.get_route(source, None)

    def get_random_route(self, source):
        """
        pick up a random route given an origin
        """
        while True:
            # different source and sink
            #### pick up a random sink from the list of sinks based on the sink selection probability ####
            selection_probability = []
            for sink in self.sinks:
                selection_probability.append(self.schedule._agents[sink].selection_probability)
            # print("self.sinks", self.sinks)
            # print("selection_probability", selection_probability)
            sink = self.random.choices(self.sinks, weights=selection_probability)[0]
            ##############################################################################################
            if sink is not source:\
                break
        return self.get_route(source, sink)

    def get_route(self, source, sink):
        if (source, sink) in self.path_ids_dict:
            return self.path_ids_dict[source, sink]
        else:
            path_ids = pd.Series(nx.shortest_path(self.G, source, sink))
            self.path_ids_dict[source, sink] = path_ids
            return path_ids

    def determine_broken_bridges(self):
        broken_bridges = set()

        flood_risk_modifiers = {0: 1.0,     # no flood prone
                                1: 1.7,     # severe river flooding
                                2: 1.3,     # moderate river flooding
                                3: 1.1,     # low river flooding
                                4: 1.8,     # severe flash flooding
                                5: 1.4,     # moderate flash flooding
                                6: 1.2,     # low flash flooding
                                7: 3.0,     # severe tidal surge
                                8: 2.5      # moderate tidal surge
                                }
        
        heavy_truck_modifiers = {
            (0, 0.02): 1.0,   
            (0.021, 0.17): 1.05,  
            (0.171, 0.28): 1.2,  
            (0.281, 0.49): 1.4,
            (0.50, 1.0): 1.8  
            }
        

        for agent in self.schedule._agents.values():
            if isinstance(agent, Bridge):
                # get base probability from scenario
                base_prob = agent.probabilities[self.scenario][agent.condition]

                if self.flood:
                    # get flood risk modifier based on flood category
                    flood_modifier = flood_risk_modifiers.get(agent.floodcat, 1.0)

                    # calculate adjusted probability
                    adjusted_prob = base_prob * flood_modifier

                elif self.heavy_truck:
                    heavy_truck_modifier = heavy_truck_modifiers.get(agent.heavy_truck, 1.0)
                    adjusted_prob = base_prob * heavy_truck_modifier

                else:
                    adjusted_prob = base_prob

                # apply probability
                if random.random() < adjusted_prob:
                    broken_bridges.add(str(agent.unique_id))
                    self.condition_list.append(agent.condition)
                    agent.broken = True  
                else:
                    agent.broken = False

        #print(f"Broken bridges for this run: {broken_bridges}")
        return broken_bridges
    
    def get_average_driving_time(self):
        if not self.driving_time:  # avoid division by zero
            return 0
        return sum(self.driving_time) / len(self.driving_time)
    
    def get_total_delay_time(self):
        '''
        Return the total waiting time of all trucks that reached a Sink (end of the road).
        '''
        return self.total_wait_time
    
    def get_broken_bridges(self):
        '''
        Return the list of broken bridges
        '''
        return list(self.broken_bridges)
    
    def get_top_10_delay(self):
        '''
        Return the 10 bridges with the biggest total delay time in a dictionary form.
            key=name of the bridge
            value=total accumulated delay time of the bridge
        If there is no bridge with delay then return a tuple
        with the first element being None (name of the bridge) and the second element being 0
        (caused delay time by that bridge).
        '''
        if not self.bridge_delays:
            return {}  # return empty dict if no bridges with delay

        # get the top 10 bridges with the highest delay
        top_10 = heapq.nlargest(10, self.bridge_delays.items(), key=lambda x: x[1])

        return dict(top_10)
    
    def get_bridge_delay_dict(self):
        '''
        Return the dictionary of bridges with their accumulated delay time
        '''
        #sort self.bridge_delays
        sorted_bridge_delays = dict(sorted(self.bridge_delays.items(), key=lambda x: x[1], reverse=True))

        return sorted_bridge_delays

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

    def step(self):
        """
        Advance the simulation by one step.
        """
        self.schedule.step()

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
# EOF -----------------------------------------------------------