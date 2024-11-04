import requests
import pandas as  pd

df = pd.read_csv('blitz_players.csv')

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
        return pd.read_csv('blitz_players.csv'), None


def get_deviation(username):
    url = f'https://lichess.org/api/user/{username}/perf/blitz'
    
    try:
        response = requests.get(url)
        if response.status_code == 429:
            rating_deviation = -1
            return "rate_limited", rating_deviation
        elif response.status_code != 200:
            rating_deviation = -1
            print(f"Failed to retrieve data for {username}. Status code: {response.status_code}")
            return "failed", rating_deviation
            
        data = response.json()
        
        #my own way i figured out, im genius
        rating_deviation = data.get('perf')
        rating_deviation = rating_deviation.get('glicko')
        rating_deviation = rating_deviation.get('deviation')
#---------------------------------------------------------------        
        #more concise way
        # rating_deviation_chat = data.get('perf', {}).get('glicko', {}).get('deviation')
        # print(rating_deviation_chat)
#---------------------------------------------------------------
        if rating_deviation is not None:
            print(f"Rating Deviation (RD) for {username} in blitz is: {rating_deviation}")
            return "success", rating_deviation
        else:
            print(f"Rating Deviation (RD) not found for {username} in blitz.")
            
    except requests.exceptions.RequestException as e:
        rating_deviation = -1
        print(f"An error occurred for user {username}: {e}")
        return "failed", -1

#-----------------------------------------------------------------------------------------------------#
#iterate this function to get user rating devitation
#rating deviation is to measure how stable a user ratin is

def add_user_stats(df):

    start_index = 0
    df, last_user_processed = load_progress()
    if last_user_processed:
        start_index = df[df['user_id'] == last_user_processed].index[0] + 1
        
    # Create empty columns for the stats
    for col in ['rating_deviation']:
        if col not in df.columns:
            df[col] = 0.0

    while start_index < len(df):
        row = df.iloc[start_index]
        user_id = row['user_id']
        status, deviation = get_deviation(user_id)

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
            df.at[start_index, 'rating_deviation'] = deviation

        # Save progress after each user and move to the next
        save_progress(df)
        start_index += 1

    # Final save to ensure all progress is written
    print("All users processed and final stats saved to deviation_stats.csv")
    
    return df

df = add_user_stats(df)
df.to_csv('deviation_stats.csv', index=False)