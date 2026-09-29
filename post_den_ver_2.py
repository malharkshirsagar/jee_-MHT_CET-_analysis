import pandas as pd

# Load the first 3 rows of your MS clean file
ms_df = pd.read_csv("mht_cet_all_india_clean.csv", nrows=3)
print("MS Clean File Columns:")
print(ms_df.columns.tolist())
