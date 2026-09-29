import pandas as pd

df = pd.read_csv("mht_cet_all_india_clean.csv", nrows=5)
print("Columns in clean CSV:", df.columns.tolist())
