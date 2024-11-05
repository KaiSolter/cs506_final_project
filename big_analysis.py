import pandas as pd

# Load the CSV file
df = pd.read_csv('alldata6.csv')

# Drop non-numeric columns
df_numeric = df.select_dtypes(include='number')

# Display basic information about the data
print("Basic Information:")
print(df_numeric.info())
print("\n")

# Generate summary statistics for numerical columns
print("Summary Statistics:")
print(df_numeric.describe())
print("\n")

# Calculate average for each numerical column
averages = df_numeric.mean()
print("Averages for each column:")
print(averages)
print("\n")

# Generate correlation matrix for the dataset
correlation_matrix = df_numeric.corr()
print("Correlation Matrix:")
print(correlation_matrix)


# Optional: Display or save the correlation matrix as a heatmap for easier analysis
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(16, 12))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
plt.title("Correlation Matrix Heatmap")
plt.show()
