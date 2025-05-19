from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from components import Source, Sink, SourceSink, Bridge, Link, Vehicle
import pandas as pd
from collections import defaultdict
import random
import csv


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

        Since there is only one road in the Demo, the paths are added with the road info;
        when there is a more complex network layout, the paths need to be managed differently

    sources: list
        all sources in the network

    sinks: list
        all sinks in the network

    """

    step_time = 1

    def __init__(self, seed=None, x_max=500, y_max=500, x_min=0, y_min=0,
                 probabilities={}, scenario=0):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []


        self.driving_times = []
        self.bridge_delays = {}  # {bridge_id: total delay time}
        self.total_wait_time = 0  # initialize total waiting time
        self.probabilities = probabilities # insert probabilities dict
        self.scenario = scenario 

        self.generate_model()
        self.broken_bridges = self.determine_broken_bridges()  # stores broken bridge IDs

    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels
        """

        df = pd.read_csv('../data/processed/demo_100.csv')

        # a list of names of roads to be generated
        roads = ['N1']

        # roads = [
        #     'N1', 'N2', 'N3', 'N4',
        #     'N5', 'N6', 'N7', 'N8'
        # ]

        df_objects_all = []
        for road in roads:

            # be careful with the sorting
            # better remove sorting by id
            # Select all the objects on a particular road

            df['numeric_id'] = df['id'].apply(lambda x: int(x.split('_')[1]))
            df_objects_on_road = df[df['road'] == road].sort_values(by=['numeric_id'])

            if not df_objects_on_road.empty:
                df_objects_all.append(df_objects_on_road)

                # the object IDs on a given road
                path_ids = df_objects_on_road['id']
                # add the path to the path_ids_dict
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                # put the path in reversed order and reindex
                path_ids = path_ids[::-1]
                path_ids.reset_index(inplace=True, drop=True)
                # add the path to the path_ids_dict so that the vehicles can drive backwards too
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids

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
            for _, row in df.iterrows():    # index, row in ...

                # create agents according to model_type
                model_type = row['model_type']
                agent = None

                if model_type == 'source':
                    agent = Source(row['id'], self, row['length'], row['name'], row['road'])
                    self.sources.append(agent.unique_id)
                elif model_type == 'sink':
                    agent = Sink(row['id'], self, row['length'], row['name'], row['road'])
                    self.sinks.append(agent.unique_id)
                elif model_type == 'sourcesink':
                    agent = SourceSink(row['id'], self, row['length'], row['name'], row['road'])
                    self.sources.append(agent.unique_id)
                    self.sinks.append(agent.unique_id)
                elif model_type == 'bridge':
                    agent = Bridge(row['id'], self, row['condition'], row['length'], row['name'], row['road'])
                elif model_type == 'link':
                    agent = Link(row['id'], self, row['length'], row['name'], row['road'])

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
            if sink is not source:
                break
        return self.path_ids_dict[source, sink]
    

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

        #print(f"Broken bridges for this run: {broken_bridges}"
        return broken_bridges

    def step(self):
        """
        Advance the simulation by one step.
        """
        self.schedule.step()


    def get_average_driving_time(self):
        if not self.driving_times:  # avoid division by zero
            return 0
        return sum(self.driving_times) / len(self.driving_times)


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
        total_trucks = len(self.driving_times)  # total trucks that reached a Sink
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
