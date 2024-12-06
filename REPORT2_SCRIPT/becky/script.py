import pandas as pd

# Load data
df = pd.read_csv('becky_user&op_stats.csv')
df2 = pd.read_csv('good_op_progress.csv')
df3 = pd.read_csv('beckyIsBlitz.csv')

# Select specific columns from df3
df3 = df3[['user_id', 'op_id', 'is_blitz']]

# Concatenate df2 and df3
df_concat = pd.concat([df2, df3], ignore_index=True)

# Merge df and df_concat
merged_df = pd.merge(df, df_concat, on="user_id", how="left", suffixes=("", "_drop"))

# Drop duplicate "op_id" column if it exists
if "op_id_drop" in merged_df.columns:
    merged_df = merged_df.drop(columns=["op_id_drop"])

# Define the final column order
final_columns = [
    "user_id", "user_win_rate", "user_lose_rate", "user_draw_rate", "user_game_count",
    "user_blitz_rating", "user_rating_bin", "op_id", "game_result", "user_rating_deviation",
    "user_blitz_total_games", "user_best_win_1", "user_best_win_2", "user_best_win_3",
    "op_rating_deviation", "op_blitz_total_games", "op_best_win_1", "op_best_win_2", 
    "op_best_win_3", "is_blitz"
]

# Filter for columns that exist
final_columns = [col for col in final_columns if col in merged_df.columns]

# Reorder columns
merged_df = merged_df[final_columns]




merged_df.to_csv('userAll.csv', index = False)