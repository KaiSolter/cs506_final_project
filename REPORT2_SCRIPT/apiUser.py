import requests
import pandas as  pd

df = pd.read_csv('../past_csv/small_sample.csv')

def save_progress(df):
    """Saves the DataFrame to progress.csv."""
    df.to_csv('progress.csv', index=False)
    print("Progress saved to progress.csv")

#continue from last user id
def load_progress():
    """Loads progress from progress.csv and identifies the last user processed."""
    try:
        progress_df = pd.read_csv('progress.csv')
        last_user_processed = progress_df['user_id'].iloc[-1]
        print(f"Resuming from user ID: {last_user_processed}")
        return progress_df, last_user_processed
    except FileNotFoundError:
        print("No progress file found. Starting from scratch.")
        return pd.read_csv('../past_csv/small_sample.csv'), None


def get_apiUser(username):
    url = f'https://lichess.org/api/user/{username}/perf/blitz'
    data = None
    
    try:
        response = requests.get(url)
        if response.status_code == 429:
            return "rate_limited", data
        elif response.status_code != 200:
            print(f"Failed to retrieve data for {username}. Status code: {response.status_code}")
            return "failed", data
            
        data = response.json()
        if data is not None:
            return "success", data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred for user {username}: {e}")
        return "failed", data
    
def deviation(data):
    return data.get('perf', {}).get('glicko', {}).get('deviation')

def total_game(data): 
    return data.get('stat', {}).get('count', {}).get('all')

def best_win(data):
    best_wins = data.get("stat", {}).get("bestWins", {}).get("results", [])
    if len(best_wins) >= 3:
        return [best_wins[0].get('opRating'), best_wins[1].get('opRating'), best_wins[2].get('opRating')]
    return [0, 0, 0]  # Default to 0 if less than 3 best wins

    

def add_user_stats(df):

    start_index = 0
    df, last_user_processed = load_progress()
    if last_user_processed:
        start_index = df[df['user_id'] == last_user_processed].index[0] + 1
        

    while start_index < len(df):
        row = df.iloc[start_index]
        user_id = row['user_id']
        status, data = get_apiUser(user_id)
        # print(data)

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
            df.at[start_index, 'user_rating_deviation'] = deviation(data)
            df.at[start_index, 'user_blitz_total_games'] = total_game(data)
            best_wins = best_win(data)
            df.at[start_index, 'user_best_win_1'] = best_wins[0]
            df.at[start_index, 'user_best_win_2'] = best_wins[1]
            df.at[start_index, 'user_best_win_3'] = best_wins[2]

        # Save progress after each user and move to the next
        save_progress(df)
        start_index += 1

    # Final save to ensure all progress is written
    print("All users processed and final stats saved to deviation_stats.csv")
    
    return df

df = add_user_stats(df)
df.to_csv('deviation_stats.csv', index=False)