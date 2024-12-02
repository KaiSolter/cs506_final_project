import pandas as pd

# Replace 'your_file.csv' with the path to your CSV file
csv_file = 'progress.csv'

# Load the CSV into a DataFrame
try:
    df = pd.read_csv(csv_file)

    # Check if 'is_blitz' column exists
    if 'is_blitz' not in df.columns:
        print("The 'is_blitz' column does not exist in the CSV file.")
    else:
        # Count occurrences of 1's and 0's
        counts = df['is_blitz'].value_counts()

        # Get counts of 1's and 0's, defaulting to 0 if not present
        num_ones = counts.get(1, 0)
        num_zeros = counts.get(0, 0)

        print(f"Number of 1's: {num_ones}")
        print(f"Number of 0's: {num_zeros}")

except FileNotFoundError:
    print(f"The file '{csv_file}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
