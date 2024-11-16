import requests
import json
import pandas as pd
import time

df = pd.read_csv('../past_csv/small_sample.csv')

#------------------------------------------------------------------------------------#
#rate limit logic

#save current progress
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
    
#--------------------------------------------------------------------------------------------#
#fetching api response logic

def get_game_json(username):
    """Get game json for a particular user"""
    url = f"https://lichess.org/api/games/user/{username}"
    params = {
        "max": 110,
        "perfType": "blitz",
        "opening": False,
        "clocks": False,
        "evals": False,
        "pgnInJson": True,
    }
    
    headers = {
        "Accept": "application/x-ndjson",
        "User-Agent": "WinRateCalculator/1.0"
    }

    response = requests.get(url, params=params, headers=headers, stream=True)
    if response.status_code == 429:
        print("Rate limit hit. Stopping process and saving progress.")
        return None
    if response.status_code != 200:
        print(f"Failed to fetch data for {username}. Error code: {response.status_code}")
        return None
    return response

#--------------------------------------------------------------------------------------------#

def get_color_specific_winrates(response, username):
    white_win_count = 0
    white_draw_count = 0
    white_loss_count = 0
    white_game_count = 0
    black_win_count = 0
    black_draw_count = 0
    black_loss_count = 0
    black_game_count = 0

    for line in response.iter_lines():
        if line:
            game = line.decode("utf-8")
            game_data = json.loads(game)
            # Games where the user is the white player
            if ("user" in game_data["players"]["white"] and
                game_data["players"]["white"]["user"]["name"].lower() == username.lower()):
                if "winner" in game_data:
                    if game_data["winner"] == "white":
                        white_win_count += 1
                    else:
                        white_loss_count += 1
                else:
                    white_draw_count += 1  # No winner field means it was a draw
                white_game_count += 1
            
            # Games where the user is the black player
            if ("user" in game_data["players"]["black"] and
                game_data["players"]["black"]["user"]["name"].lower() == username.lower()):
                if "winner" in game_data:
                    if game_data["winner"] == "black":
                        black_win_count += 1
                    else:
                        black_loss_count += 1
                else:
                    black_draw_count += 1  # No winner field means it was a draw
                black_game_count += 1
                
    if white_game_count == 0:
        print(f"No blitz games found for user: {username} as black.")
        white_win_rate = 0
        white_lose_rate = 0
        white_draw_rate = 0
    else:
        white_win_rate = (white_win_count / white_game_count) * 100
        white_lose_rate = (white_loss_count / white_game_count) * 100
        white_draw_rate = (white_draw_count / white_game_count) * 100

    if black_game_count == 0:
        print(f"No blitz games found for user: {username} as black.")
        black_win_rate = 0
        black_lose_rate = 0
        black_draw_rate = 0
    else:
        black_win_rate = (black_win_count / black_game_count) * 100
        black_lose_rate = (black_loss_count / black_game_count) * 100
        black_draw_rate = (black_draw_count / black_game_count) * 100
    return white_win_rate, white_lose_rate, white_draw_rate, white_game_count, black_win_rate, black_lose_rate, black_draw_rate, black_game_count

#--------------------------------------------------------------------------------------------#

def get_game_data(username):
    response = get_game_json(username)
    if response == None: 
        return None
    elif response.status_code == 429:
        return "rate_limited"

    white_win_rate, white_lose_rate, white_draw_rate, white_game_count, black_win_rate, black_lose_rate, black_draw_rate, black_game_count = get_color_specific_winrates(response, username)
    return "success", white_win_rate, white_lose_rate, white_draw_rate, white_game_count, black_win_rate, black_lose_rate, black_draw_rate, black_game_count
    
#--------------------------------------------------------------------------------------------#

def add_user_stats(df):
    results_df, last_user_processed = load_progress()
    start_index = 0
    if last_user_processed:
        try:
            start_index = df[df['user_id'] == last_user_processed].index[0] + 1
        except IndexError:
            start_index = 0

    total_users = len(df)
    for index, row in df.iloc[start_index:].iterrows():
        username = row['user_id']
        print(f"Processing user {index+1}/{total_users}: {username}")
        status, white_win_rate, white_lose_rate, white_draw_rate, white_game_count, black_win_rate, black_lose_rate, black_draw_rate, black_game_count = get_game_data(username)
        
        if status == "rate_limited":
            save_progress(df)
            time.sleep(120)
            continue
        elif status == "success":
            df.at[index, 'white_win_rate'] = white_win_rate
            df.at[index, 'white_lose_rate'] = white_lose_rate
            df.at[index, 'white_draw_rate'] = white_draw_rate
            df.at[index, 'white_game_count'] = white_game_count
            df.at[index, 'black_win_rate'] = black_win_rate
            df.at[index, 'black_lose_rate'] = black_lose_rate
            df.at[index, 'black_draw_rate'] = black_draw_rate
            df.at[index, 'black_game_count'] = black_game_count
        else:
            print(f"Skipping user {username} due to fetch error.")
            df.at[index, 'white_win_rate'] = 0
            df.at[index, 'white_lose_rate'] = 0
            df.at[index, 'white_draw_rate'] = 0
            df.at[index, 'white_game_count'] = 0
            df.at[index, 'black_win_rate'] = 0
            df.at[index, 'black_lose_rate'] = 0
            df.at[index, 'black_draw_rate'] = 0
            df.at[index, 'black_game_count'] = 0
        print("Saving progress")
        save_progress(df)
    return df

#--------------------------------------------------------------------------------------------#

# Run the function and save the results to a new CSV file
df, _ = load_progress()
df = add_user_stats(df)
df.to_csv('final.csv', index=False)
