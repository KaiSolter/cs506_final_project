import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = 'final_stats.csv'  # Adjust the path as necessary
data = pd.read_csv(file_path)

# Basic statistics
print("Summary Statistics:")
print(data.describe())

# Count of users with 0 in win_rate, lose_rate, and draw_rate
zero_rate_count = data[(data['win_rate'] == 0) & (data['lose_rate'] == 0) & (data['draw_rate'] == 0)].shape[0]
print(f"Number of users with 0 in win_rate, lose_rate, and draw_rate: {zero_rate_count}")

# Histograms for rating and win/lose/draw rates
plt.figure(figsize=(12, 8))

# Blitz Rating Distribution
plt.subplot(2, 2, 1)
plt.hist(data['blitz_rating'], bins=30, edgecolor='black')
plt.title('Blitz Rating Distribution')
plt.xlabel('Blitz Rating')
plt.ylabel('Frequency')

# Win Rate Distribution
plt.subplot(2, 2, 2)
plt.hist(data['win_rate'], bins=30, color='green', edgecolor='black')
plt.title('Win Rate Distribution')
plt.xlabel('Win Rate (%)')
plt.ylabel('Frequency')

# Lose Rate Distribution
plt.subplot(2, 2, 3)
plt.hist(data['lose_rate'], bins=30, color='red', edgecolor='black')
plt.title('Lose Rate Distribution')
plt.xlabel('Lose Rate (%)')
plt.ylabel('Frequency')

# Draw Rate Distribution
plt.subplot(2, 2, 4)
plt.hist(data['draw_rate'], bins=30, color='blue', edgecolor='black')
plt.title('Draw Rate Distribution')
plt.xlabel('Draw Rate (%)')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()

# Scatter plot of Blitz Rating vs. Game Count
plt.figure(figsize=(8, 6))
plt.scatter(data['blitz_rating'], data['game_count'], alpha=0.5)
plt.title('Blitz Rating vs Game Count')
plt.xlabel('Blitz Rating')
plt.ylabel('Game Count')
plt.show()