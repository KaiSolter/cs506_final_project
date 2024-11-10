import pandas as pd

# Read the CSV files
df1 = pd.read_csv('.csv')
df2 = pd.read_csv('file2.csv')

import pandas as pd

# Assuming df1 and df2 are your DataFrames
merged_df = pd.merge(df1, df2, on="user_id", suffixes=("", "_dup"))

# Drop the duplicated columns created during the merge
merged_df = merged_df.loc[:, ~merged_df.columns.str.endswith("_dup")]
