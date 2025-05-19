from model import BangladeshModel
import pandas as pd
import random
import numpy as np
"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
days = 5
run_length = 24 * 60 * days

scenario = {
    0: {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.0},
    1: {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.05},
    2: {'A': 0.0, 'B': 0.0, 'C': 0.05, 'D': 0.1},
    3: {'A': 0.0, 'B': 0.05, 'C': 0.1, 'D': 0.2},
    4: {'A': 0.05, 'B': 0.1, 'C': 0.2, 'D': 0.4},
}

scenario_range = len(scenario)
replications = 10

seeds = (np.random.randint(100000, 999999, size=replications)) # 5 scenarios

for n in range(scenario_range):

    data_list = []
    
    for seed in seeds:
        sim_model = BangladeshModel(seed=int(seed), probabilities=scenario, scenario=n)
        print(f"Running scenario {n} with seed {seed}")

        for i in range(run_length):
            sim_model.step()

        data_list.append({
                    'Scenario': n,
                    'Seed': seed,
                    'Average_driving_time': sim_model.get_average_driving_time(),
                    'Total_waiting_time': sim_model.get_total_delay_time(),
                    'Average_waiting_time': sim_model.get_average_delay_time(),
                    #'Categories'    : ', '.join(sim_model.condition_list),
                    'Broken_bridges': ', '.join(sim_model.get_broken_bridges()),
                    'Average Speed': sim_model.get_average_effective_speed()
                })

        df = pd.DataFrame(data_list)

        # save to csv
        df.to_csv(f'../experiment/scenario{n}.csv', index=False)
