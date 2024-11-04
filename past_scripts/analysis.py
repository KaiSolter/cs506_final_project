import pandas as pd
import matplotlib.pyplot as plt

# Load your CSV data
df = pd.read_csv("lichess_user_ratings.csv")

# Drop any rows with missing values in 'blitz_rating' if needed
df = df.dropna(subset=['blitz_rating'])

# Calculate summary statistics
mean_rating = df['blitz_rating'].mean()
median_rating = df['blitz_rating'].median()
std_dev_rating = df['blitz_rating'].std()

# Display summary statistics
print(f"Mean Rating: {mean_rating}")
print(f"Median Rating: {median_rating}")
print(f"Standard Deviation: {std_dev_rating}")

# Plot distribution of blitz_rating
plt.figure(figsize=(10, 6))
plt.hist(df['blitz_rating'], bins=30, edgecolor='black', alpha=0.7)
plt.axvline(mean_rating, color='red', linestyle='dashed', linewidth=1, label=f'Mean: {mean_rating:.2f}')
plt.axvline(median_rating, color='blue', linestyle='dashed', linewidth=1, label=f'Median: {median_rating:.2f}')
plt.xlabel("Blitz Rating")
plt.ylabel("Frequency")
plt.title("Distribution of Blitz Ratings")
plt.legend()
plt.show()
