import pandas as pd
import requests
import time
import json

INPUT_CSV = 'tiafinal&op2.csv'
OUTPUT_CSV = 'tiaIsBlitz.csv'
PROGRESS_FILE = 'progress.csv'
API_DELAY = 1
MAX_GAMES = 300

def save_progress(df):
    """Saves the DataFrame to progress.csv."""
    df.to_csv(PROGRESS_FILE, index=False)
    print("Progress saved to progress.csv.")

def load_progress():
    """Loads progress from progress.csv and identifies the last user processed."""
    try:
        progress_df = pd.read_csv(PROGRESS_FILE)
        last_user_processed = progress_df.iloc[-1]['user_id']
        print(f"Resuming from user ID: {last_user_processed}")
        return progress_df, last_user_processed
    except FileNotFoundError:
        print("No progress file found. Starting from scratch.")
        return pd.read_csv(INPUT_CSV), None

def check_blitz_game(user1, user2):
    """Checks if there exists a blitz game between user1 and user2."""
    url = f"https://lichess.org/api/games/user/{user1}"
    headers = {"Accept": "application/x-ndjson"}
    params = {"perfType": "blitz", "max": MAX_GAMES, "pgnInJson": "true"}
    try:
        response = requests.get(url, headers=headers, params=params, stream=True)
        if response.status_code == 429:
            print("Rate limit hit. Saving progress...")
            return "rate_limit"
        if response.status_code != 200:
            return False
        for line in response.iter_lines():
            if line:
                game = line.decode('utf-8')
                game_data = json.loads(game)
                white = game_data.get('players', {}).get('white', {}).get('user', {}).get('name', '').lower()
                black = game_data.get('players', {}).get('black', {}).get('user', {}).get('name', '').lower()
                if user2.lower() == white or user2.lower() == black:
                    return True
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False
    return False

df, last_user_processed = load_progress()

if 'is_blitz' not in df.columns:
    df['is_blitz'] = 0

start_index = 0
if last_user_processed:
    try:
        start_index = df[df['user_id'] == last_user_processed].index[-1] + 1
    except IndexError:
        print("Last user processed not found in the current dataset. Starting from the beginning.")

for index in range(start_index, len(df)):
    row = df.iloc[index]
    user1 = row['user_id']
    user2 = row['op_id']
    result = check_blitz_game(user1, user2)
    if result == "rate_limit":
        save_progress(df)
        print("Rate limit encountered. Pausing for 60 seconds...")
        time.sleep(60)
        continue
    df.at[index, 'is_blitz'] = 1 if result else 0
    save_progress(df)
    time.sleep(API_DELAY)

df.to_csv(OUTPUT_CSV, index=False)
print(f"Updated CSV saved to '{OUTPUT_CSV}'.")
