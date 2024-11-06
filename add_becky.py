import pandas as pd

df1 = pd.read_csv('tia-feature-full.csv')
df2 = pd.read_csv('becky_stats.csv')

# Perform the merge on 'user_id', with custom suffixes to avoid duplicates
merged_df = pd.merge(df1, df2, on='user_id', how='left', suffixes=('', '_dup'))

# Drop any columns with the '_dup' suffix that may have come from df2, if they already exist in df1
merged_df = merged_df.loc[:, ~merged_df.columns.str.endswith('_dup')]

# Define the current column order
current_columns = [
    'user_id', 'blitz_rating', 'win_rate', 'lose_rate', 'draw_rate', 
    'game_count', 'rating_deviation', 'user_op', 'game_result', 
    'op_rating_deviation', 'op_win_rate', 'op_lose_rate', 'op_draw_rate', 'op_game_count'
]

# Define the new columns from df2 that you want to insert after 'game_count'
new_columns = ['black_win_rate', 'black_lose_rate', 'black_draw_rate', 'black_game_count']

# Find the index of 'game_count' to insert new columns after it
insert_position = current_columns.index('game_count') + 1

# Insert new columns into the desired position in the column order
ordered_columns = current_columns[:insert_position] + new_columns + current_columns[insert_position:]

# Reorder merged_df using the new column order
merged_df = merged_df[ordered_columns]

merged_df.to_csv('tia&beck.csv', index = False)
