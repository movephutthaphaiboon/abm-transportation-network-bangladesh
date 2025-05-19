from model import BangladeshModel
import numpy as np
import pandas as pd

"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
# run_length = 5 * 24 * 60

# run time (ticks)
run_length = 7200

scenario = {
    0: {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.0},
    1: {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.05},
    2: {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.10},
    3: {'A': 0.0, 'B': 0.0, 'C': 0.05, 'D': 0.10},
    4: {'A': 0.0, 'B': 0.0, 'C': 0.10, 'D': 0.20},
    5: {'A': 0.0, 'B': 0.05, 'C': 0.10, 'D': 0.20},
    6: {'A': 0.0, 'B': 0.10, 'C': 0.20, 'D': 0.40},
    7: {'A': 0.05, 'B': 0.10, 'C': 0.20, 'D': 0.40},
    8: {'A': 0.10, 'B': 0.20, 'C': 0.40, 'D': 0.80}
}

scenario_range = len(scenario)

# Check if the seed is set
#print("SEED " + str(sim_model._seed))

for n in range(scenario_range):

    seeds = np.random.randint(100000, 999999, size=10) # 10 scenarios

    data_list = []
    
    for seed in seeds:
        sim_model = BangladeshModel(seed=int(seed), probabilities=scenario, scenario=n)

        for i in range(run_length):
            sim_model.step()

        data_list.append({
                    'Road': 'N1',
                    'Scenario': n,
                    'Seed': seed,
                    'Average_driving_time': sim_model.get_average_driving_time(),
                    'Total_waiting_time': sim_model.get_total_delay_time(),
                    'Average_waiting_time': sim_model.get_average_delay_time(),
                    'Broken_bridges': ', '.join(sim_model.get_broken_bridges()),

                })

        df = pd.DataFrame(data_list)

        # save to csv
        df.to_csv(f'../experiment/scenario{n}.csv', index=False)