import requests
import pandas as pd
import json
import time

df = pd.read_csv('deviation_stats.csv')

def save_progress(df):
    """Saves the DataFrame to progress_op.csv."""
    df.to_csv('progress_op.csv', index=False)
    print("Progress saved to progress_op.csv")

#continue from last user id
def load_progress():
    """Loads progress from progress_op.csv and identifies the last user processed."""
    try:
        progress_df = pd.read_csv('progress_op.csv')
        last_user_processed = progress_df['user_id'].iloc[-1]
        print(f"Resuming from user ID: {last_user_processed}")
        return progress_df, last_user_processed
    except FileNotFoundError:
        print("No progress file found. Starting from scratch.")
        return pd.read_csv('deviation_stats.csv'), None


headers = {"Accept": "application/x-ndjson"} 

def get_recent_op(username): 
    url = "https://lichess.org/api/games/user/" + username
    try:
        response = requests.get(url)
        if response.status_code == 429:
            return "rate_limited", None, None
        elif response.status_code != 200:
            print(f"Failed to retrieve data for {username}. Status code: {response.status_code}")
            return "failed", None, None
        

        for line in response.iter_lines():
            if line:
                try:
                    game_data = json.loads(line.decode('utf-8'))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    continue  
                # Add the usernames of white and black players
                if "players" in game_data:
                    white_player = game_data["players"].get("white", {}).get("user", {}).get("name")
                    black_player = game_data["players"].get("black", {}).get("user", {}).get("name")

                    if white_player == username: 
                        op = black_player
                        if game_data["winner"] == "white":
                            score = 1
                        elif game_data["winner"] == "black":
                            score = -1
                        else:
                            score = 0
                    elif black_player == username:
                        op = white_player
                        if game_data["winner"] == "white":
                            score = -1
                        elif game_data["winner"] == "black":
                            score = 1
                        else:
                            score = 0
                return "success", op, score
    except requests.exceptions.RequestException as e:
        print(f"An error occurred for user {username}: {e}")
        return "failed", None, None
        
#---------------------------------------------------------------------------
#iterate this function to get opponent and game result
#this is to get the results (label) of our dataset.

def add_user_stats(df):

    start_index = 0
    df, last_user_processed = load_progress()
    if last_user_processed:
        start_index = df[df['user_id'] == last_user_processed].index[0] + 1
        
    # Create empty columns for the stats
    for col in ['user_op']:
        if col not in df.columns:
            df[col] = ""
    
    for col in ['game_result']:
        if col not in df.columns:
            df[col] = 401   

    while start_index < len(df):
        row = df.iloc[start_index]
        user_id = row['user_id']
        print(user_id)
        status, op, score = get_recent_op(user_id)

        if status == "rate_limited":
            # Save progress and restart the loop to retry
            save_progress(df)
            print("Rate limit encountered. Retrying...")
            continue
        elif status == "failed":
            print(f"Failed to retrieve data for {user_id}. Moving to next user.")
            start_index += 1
        else:
            # Update stats if successful
            df.at[start_index, 'user_op'] = op
            df.at[start_index, 'game_result'] = score


        # Save progress after each user and move to the next
        save_progress(df)
        start_index += 1

    # Final save to ensure all progress is written
    print("All users processed and final stats saved to deviation_stats.csv")
    
    return df

df = add_user_stats(df)
df.to_csv('user_op_update.csv', index=False)