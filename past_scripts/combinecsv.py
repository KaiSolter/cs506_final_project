import pandas as pd

# Read the CSV files
df1 = pd.read_csv('file1.csv')
df2 = pd.read_csv('file2.csv')

# Remove duplicates based on the first column (assuming it's the 'UserID' column)
df1 = df1.drop_duplicates(subset=df1.columns[0], keep='first')
df2 = df2.drop_duplicates(subset=df2.columns[0], keep='first')

# Combine the dataframes
combined_df = pd.concat([df1, df2])

# Remove any duplicates that might arise from combining
combined_df = combined_df.drop_duplicates(subset=combined_df.columns[0], keep='first')

# Save to a new CSV file
combined_df.to_csv('combined.csv', index=False)
