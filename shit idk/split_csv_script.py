import pandas as pd


# Load the CSV file
input_file = 'COPY_completeUserIds_5.csv'  # Replace with your CSV file name
data = pd.read_csv(input_file)


# Determine the number of rows per split
num_splits = 2
rows_per_split = len(data) // num_splits


# Split and save each part as a separate CSV
for i in range(num_splits):
    start = i * rows_per_split
    # If it's the last split, capture all remaining rows
    end = (i + 1) * rows_per_split if i < num_splits - 1 else len(data)
    split_data = data.iloc[start:end]
    split_data.to_csv(f'beckys_user_ids_{i+1}.csv', index=False)


