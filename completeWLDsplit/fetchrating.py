import pandas as pd
import requests
import time

def save_progress(df):
    """Saves the DataFrame to progress.csv."""
    df.to_csv('save.csv', index=False)
    print("Progress saved to csv")

#continue from last user id
def load_progress():
    """Loads progress from progress.csv and identifies the last user processed."""
    try:
        progress_df = pd.read_csv('save.csv')
        last_user_processed = progress_df['user_id'].iloc[-1]
        print(f"Resuming from user ID: {last_user_processed}")
        return progress_df, last_user_processed
    except FileNotFoundError:
        print("No progress file found. Starting from scratch.")
        return pd.read_csv('completewld_1.csv'), None

def fetch_user_rating(user_id):
    url = f"https://lichess.org/api/user/{user_id}"
    headers = {
        'Accept': 'application/json',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 429:
            print(f"Rate limited. Waiting {30} seconds...")
            time.sleep(30)
            return "failure", None
        elif response.status_code != 200:
                print(f"Failed to retrieve data for {user_id}. Status code: {response.status_code}")
                return "failure", None
        response.raise_for_status()
        data = response.json()
        
        blitz = data.get('perfs', {}).get('blitz', {})
        rating = blitz.get('rating', None)
        
        return "success", rating
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error for {user_id}: {http_err}")

def add_user_ratings(df):
    start_index = 0
    df, last_user_processed = load_progress()
    if last_user_processed:
        start_index = df[df['user_id'] == last_user_processed].index[0] + 1
        
    # Create empty columns for the stats
    df['blitz_rating'] = 0.0

    while start_index < len(df):
        row = df.iloc[start_index]
        user_id = row['user_id']
        status, blitz_rating = fetch_user_rating(user_id)

        if status == "rate_limited":
            # Save progress and restart the loop to retry
            save_progress(df)
            print("Rate limit encountered. Retrying...")
            continue
        elif status == "failed":
            print(f"Failed to retrieve data for {user_id}. Moving to next user.")
            start_index += 1
            continue
        elif status == "no_games":
            print(f"No Blitz games for {user_id}. Moving to next user.")
        else:
            # Update stats if successful
            df.at[start_index, 'blitz_rating'] = blitz_rating

        # Save progress after each user and move to the next
        save_progress(df)
        start_index += 1

    # Final save to ensure all progress is written
    df.to_csv('final.csv', index=False)
    print("All users processed and final stats saved to final.csv")
    
    return df

df = pd.read_csv('completewld_1.csv')
df, _ = load_progress()
df = add_user_ratings(df)
df.to_csv('final.csv', index=False)