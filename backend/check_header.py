
import pandas as pd
df = pd.read_csv('mumbai_multi_route_traffic_dataset_FINAL_1LAKH.csv', nrows=1)
with open('header.txt', 'w') as f:
    for col in df.columns:
        f.write(col + '\n')
