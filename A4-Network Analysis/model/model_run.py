from model import BangladeshModel
import numpy as np
import pandas as pd

"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
days = 3
run_length = 24 * 60 * days

scenario = {
    0: {'A': 0.01, 'B': 0.05, 'C': 0.15, 'D': 0.30},
    1: {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.0},
}

configurations = [
    {'flood': False, 'heavy_truck': False},
    {'flood': True, 'heavy_truck': False},
    {'flood': False, 'heavy_truck': True}
]

scenario_range = len(scenario)
replications = 100

seeds = (np.random.randint(100000, 999999, size=replications))

for config in configurations:
    flood = config['flood']
    heavy_truck = config['heavy_truck']

    for n in range(scenario_range):

        data_list = []
        
        for seed in seeds:
            sim_model = BangladeshModel(seed=int(seed), probabilities=scenario, scenario=n, 
                                        flood=flood, heavy_truck=heavy_truck)
            print(f"Running scenario {n} with seed {seed}")

            for i in range(run_length):
                sim_model.step()

            data_list.append({
                        'Scenario': n,
                        'Seed': seed,
                        'Average_driving_time': sim_model.get_average_driving_time(),
                        'Total_waiting_time': sim_model.get_total_delay_time(),
                        'Average_waiting_time': sim_model.get_average_delay_time(),
                        #'Broken_bridges': ', '.join(sim_model.get_broken_bridges()),
                        #'Top 10 delays': sim_model.get_top_10_delay(),
                        'Delay dict': sim_model.get_bridge_delay_dict(),
                        #'Categories'    : ', '.join(sim_model.condition_list),
                    })

            df = pd.DataFrame(data_list)

            # save to csv
            df.to_csv(f'../data/scenario{n}_flood{flood}_heavy_truck{heavy_truck}.csv', index=False)