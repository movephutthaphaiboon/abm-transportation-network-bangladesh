import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import boxplot, savefig
#import seaborn as sns

#%%

csv_files = ['../experiment/scenario0.csv', '../experiment/scenario1.csv', '../experiment/scenario2.csv',
             '../experiment/scenario3.csv','../experiment/scenario4.csv', '../experiment/scenario5.csv',
             '../experiment/scenario6.csv','../experiment/scenario7.csv', '../experiment/scenario8.csv']


data_list = []


for file in csv_files:
    df = pd.read_csv(file)


    data_list.append((df['Average_driving_time']/60).tolist())


plt.figure(figsize=(12, 6))
plt.boxplot(data_list, patch_artist=True)


plt.xticks(range(1, 10), [f"Scenario {i}" for i in range(9)], rotation=45)
plt.title("Boxplot of All Scenarios")
plt.ylabel("Average driving time (hours)")

savefig('../img/outputboxplot2.png')

# Show the plot
plt.show()




