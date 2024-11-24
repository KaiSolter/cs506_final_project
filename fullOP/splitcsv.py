import pandas as pd

# Load the CSV file
df = pd.read_csv('../fullDistribution/1550mean.csv')  # Replace with your CSV file name

# Split the DataFrame into three equal parts
split_1 = df[:len(df) // 3]
split_2 = df[len(df) // 3:2 * len(df) // 3]
split_3 = df[2 * len(df) // 3:]

# Save each part to a new CSV file
split_1.to_csv('split_part_1.csv', index=False)
split_2.to_csv('split_part_2.csv', index=False)
split_3.to_csv('split_part_3.csv', index=False)

print("CSV split into three parts successfully!")
