import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV file
df = pd.read_csv('allfeaturesfinal.csv')

# Select relevant features (replace with actual relevant columns)
relevant_features = [
    'user_black_game_count', 'user_black_draw_rate', 'user_black_win_rate',
    'user_blitz_rating', 'user_draw_rate', 'user_game_count', 'user_highest_blitz_opponent_rating',
    'user_win_rate', 'user_rating_deviation', 'user_total_games_played',
    'user_white_draw_rate', 'user_white_game_count', 'user_white_win_rate',
    'op_black_game_count', 'op_black_draw_rate', 'op_black_win_rate',
    'op_blitz_rating', 'op_draw_rate', 'op_game_count', 'op_highest_blitz_opponent_rating',
    'op_win_rate', 'op_rating_deviation', 'op_total_games_played',
    'op_white_draw_rate', 'op_white_game_count', 'op_white_win_rate', 'game_result'
]
df_relevant = df[relevant_features]

# Display basic information about the relevant data
print("Basic Information:")
print(df_relevant.info())
print("\n")

# Generate summary statistics for numerical columns
print("Summary Statistics:")
print(df_relevant.describe())
print("\n")

# Calculate average for each numerical column
averages = df_relevant.mean()
print("Averages for each column:")
print(averages)
print("\n")

# Generate correlation matrix for the dataset
correlation_matrix = df_relevant.corr()
print("Correlation Matrix:")
print(correlation_matrix)

# Display the correlation matrix as a heatmap with better readability
plt.figure(figsize=(18, 16))  # Increase figure size for readability
sns.heatmap(
    correlation_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    cbar=True,
    annot_kws={"size": 8}  # Set annotation font size
)

# Rotate labels for readability
plt.xticks(rotation=45, ha="right", fontsize=10)
plt.yticks(rotation=0, fontsize=10)

# Add a title
plt.title("Correlation Matrix Heatmap", fontsize=14)

# Show the plot
plt.show()
