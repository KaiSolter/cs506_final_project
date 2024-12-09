import pandas as pd

# Load Dataset 1
dataset1 = pd.read_csv('beckyGOOD/updated_op_apiGames_becky.csv')

# Load List 2 (users to remove)
list2 = pd.read_csv('REPORT2_SCRIPT/BeckyBadOPS.csv')

# Convert the 'user_id' column in List 2 to a set for faster lookup
users_to_remove = set(list2['user_id'])

# Filter Dataset 1 to exclude users present in List 2
filtered_dataset1 = dataset1[~dataset1['user_id'].isin(users_to_remove)]

# Save the filtered Dataset 1 to a new CSV file
filtered_dataset1.to_csv('filtered_dataset1.csv', index=False)

print("Filtered Dataset 1 has been saved to 'filtered_dataset1.csv'.")
