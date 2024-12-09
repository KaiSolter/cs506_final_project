import pandas as pd

# Load the CSV files
becky_clean_csv_path = 'beckyGOOD/op_apiGames_becky.csv'  # Update with your path
first_try_user_api_path = 'beckyGOOD/first_try_user_api.csv'  # Update with your path
output_file_path = 'BeckyCleanCSV_specific_order.csv'  # Update with desired output path

clean_csv = 'beckyGOOD/BeckyCleanCSV.csv'

# Read the data into dataframes
becky_clean_df = pd.read_csv(becky_clean_csv_path)
first_try_user_api_df = pd.read_csv(first_try_user_api_path)
clean_csv_df = pd.read_csv(clean_csv)

# Filter first_try_user_api_df to include only rows where user_id is in BeckyCleanCSV
filtered_user_api_df = first_try_user_api_df[first_try_user_api_df['user_id'].isin(clean_csv_df['user_id'])]


# Merge the dataframes (adjust the 'on' parameter for your join key)
merged_df = pd.concat([filtered_user_api_df, becky_clean_df.reset_index(drop=True)], axis=1)

# Save the merged DataFrame to a CSV
merged_df.to_csv(output_file_path, index=False)




