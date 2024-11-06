import pandas as pd

# Load the dataset
df = pd.read_csv('allfeaturesfinal.csv')

game_count_columns = [
    'user_black_game_count',
    'user_game_count',
    'user_white_game_count',
    'op_black_game_count',
    'op_game_count',
    'op_white_game_count'
]

# Filter out rows where any of the 'game_count' columns have a zero
for column in game_count_columns:
    df = df[df[column] != 0]

# Define columns that contain 'game_count'
game_count_columns1 = [
    'user_game_count',
    'op_game_count',
]

# Filter out rows where any of the 'game_count' columns have a value less than 10
for column in game_count_columns1:
    df = df[df[column] >= 10]

# Save the cleaned dataset
df.to_csv('finaldata_clean.csv', index=False)
