import pandas as pd

# Load the dataset
df = pd.read_csv('allfeaturesfinal.csv')

# Remove rows with NaN values in any column
df = df.dropna()

game_count_columns = [
    'user_black_game_count',
    'user_game_count',
    'user_white_game_count',
    'op_black_game_count',
    'op_game_count',
    'op_white_game_count',
    'user_total_games_played',
    'op_total_games_played'
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

# Remove rows where 'user_rating_deviation' or 'op_rating_deviation' are 0 or 500
df = df[(df['user_rating_deviation'] != 0) & (df['user_rating_deviation'] != 500) &
        (df['op_rating_deviation'] != 0) & (df['op_rating_deviation'] != 500)]

# Save the cleaned dataset
df.to_csv('finaldata_clean.csv', index=False)
