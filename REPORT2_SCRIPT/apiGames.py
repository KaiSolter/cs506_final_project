import requests
from requests.exceptions import ChunkedEncodingError
import json
import pandas as pd
import time

df = pd.read_csv('../KaiUserStatswld1.csv')

#------------------------------------------------------------------------------------#
#rate limit/ saving progress logic

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
        return pd.read_csv('../KaiUserStatswld1.csv'), None
    
#--------------------------------------------------------------------------------------------#
#fetching api response logic

def get_game_json(username):
    """Get game json for a particular user"""
    url = f"https://lichess.org/api/games/user/{username}"
    params = {
        "max": 110,
        "perfType": "blitz",
        "opening": True,
        "clocks": True,
        "evals": False,
        "pgnInJson": True,
    }
    
    headers = {
        "Accept": "application/x-ndjson",
        "User-Agent": "WinRateCalculator/1.0"
    }
    
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, params=params, headers=headers, stream=True, timeout=10)
            if response.status_code == 429:
                print("Rate limit hit. Stopping process and saving progress.")
                return None
            if response.status_code != 200:
                print(f"Failed to fetch data for {username}. Error code: {response.status_code}")
                return None
            return response
        except ChunkedEncodingError:
            retries += 1
            print(f"ChunkedEncodingError encountered. Retrying {retries}/{max_retries}...")
            time.sleep(2)  # Pause before retrying
    print(f"Failed to fetch data for {username} after {max_retries} retries.")
    return None

#--------------------------------------------------------------------------------------------#
#Color specific winrates

def get_color_specific_winrates(lines, username):
    white_win_count = 0
    white_draw_count = 0
    white_loss_count = 0
    white_game_count = 0
    black_win_count = 0
    black_draw_count = 0
    black_loss_count = 0
    black_game_count = 0

    for game in lines:
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
        white_win_rate = round((white_win_count / white_game_count) * 100, 3)
        white_lose_rate = round((white_loss_count / white_game_count) * 100, 3)
        white_draw_rate = round((white_draw_count / white_game_count) * 100, 3)

    if black_game_count == 0:
        print(f"No blitz games found for user: {username} as black.")
        black_win_rate = 0
        black_lose_rate = 0
        black_draw_rate = 0
    else:
        black_win_rate = round((black_win_count / black_game_count) * 100, 3)
        black_lose_rate = round((black_loss_count / black_game_count) * 100, 3)
        black_draw_rate = round((black_draw_count / black_game_count) * 100, 3)
    return white_win_rate, white_lose_rate, white_draw_rate, white_game_count, black_win_rate, black_lose_rate, black_draw_rate, black_game_count

#--------------------------------------------------------------------------------------------#
#ECO opening data

def get_ECO_data(lines, username):
    ECO_counts = {}
    ECO_wins = {}
    ECO_winrates = {}
    for game in lines:
        game_data = json.loads(game)
        if "opening" in game_data and "eco" in game_data["opening"]:
            eco = game_data["opening"]["eco"]
        else:
            eco = 'nonStandard'
        ECO_counts[eco] = ECO_counts.get(eco, 0) + 1
        
        if 'winner' in game_data and 'players' in game_data:
            white_user = game_data["players"]["white"].get("user", {}).get("name", "").lower()
            black_user = game_data["players"]["black"].get("user", {}).get("name", "").lower()

            if game_data["winner"] == "white" and username.lower() == white_user:
                ECO_wins[eco] = ECO_wins.get(eco, 0) + 1
            elif game_data["winner"] == "black" and username.lower() == black_user:
                ECO_wins[eco] = ECO_wins.get(eco, 0) + 1
                ECO_winrates = {}
    for eco, count in ECO_counts.items():
        wins = ECO_wins.get(eco, 0)
        ECO_winrates[eco] = round((wins / count) * 100, 3) if count > 0 else 0
        
    sorted_eco = sorted(ECO_counts.items(), key=lambda item: item[1], reverse=True)
    top_eco = sorted_eco[0][0] if len(sorted_eco) > 0 else None
    second_eco = sorted_eco[1][0] if len(sorted_eco) > 1 else None
        
    sorted_winrates = sorted(ECO_winrates.items(), key=lambda item: item[1], reverse=True)
    top_winrate_eco = sorted_winrates[0][0] if len(sorted_winrates) > 0 else None
    second_winrate_eco = sorted_winrates[1][0] if len(sorted_winrates) > 1 else None

    return top_eco, second_eco, top_winrate_eco, second_winrate_eco
            
#--------------------------------------------------------------------------------------------#
#Losses by time

def get_gameEnd_data(lines, username):
        total_wins = 0
        total_losses = 0
        mate_win = 0
        resign_win = 0
        time_win = 0
        mate_loss = 0
        resign_loss = 0
        time_loss = 0
        for game in lines:
            game_data = json.loads(game)
            if "status" in game_data and "winner" in game_data and "players" in game_data:
                white_user = game_data["players"]["white"].get("user", {}).get("name", "").lower()
                black_user = game_data["players"]["black"].get("user", {}).get("name", "").lower()

                if game_data["winner"] == "white" and username.lower() == white_user:
                    total_wins += 1
                    if game_data["status"] == "mate":
                        mate_win += 1
                    elif game_data["status"] == "resign":
                        resign_win += 1
                    elif game_data["status"] == "outoftime":
                        time_win += 1

                elif game_data["winner"] == "black" and username.lower() == black_user:
                    total_wins += 1
                    if game_data["status"] == "mate":
                        mate_win += 1
                    elif game_data["status"] == "resign":
                        resign_win += 1
                    elif game_data["status"] == "outoftime":
                        time_win += 1

                elif username.lower() == white_user or username.lower() == black_user:
                    total_losses += 1
                    if game_data["status"] == "mate":
                        mate_loss += 1
                    elif game_data["status"] == "resign":
                        resign_loss += 1
                    elif game_data["status"] == "outoftime":
                        time_loss += 1

        mate_winrate = round(mate_win / total_wins, 3) if total_wins > 0 else 0
        resign_winrate = round(resign_win / total_wins, 3) if total_wins > 0 else 0
        time_winrate = round(time_win / total_wins, 3) if total_wins > 0 else 0
        mate_lossrate = round(mate_loss / total_losses, 3) if total_losses > 0 else 0
        resign_lossrate = round(resign_loss / total_losses, 3) if total_losses > 0 else 0
        time_lossrate = round(time_loss / total_losses, 3) if total_losses > 0 else 0     
        return mate_winrate, resign_winrate, time_winrate, mate_lossrate, resign_lossrate, time_lossrate
            
#--------------------------------------------------------------------------------------------#
#Get average game length

def get_game_lengths(lines):
    durations = []
    for game in lines:
        game_data = json.loads(game)
        created_at = game_data.get("createdAt")
        last_move_at = game_data.get("lastMoveAt")
        
        if created_at is None or last_move_at is None:
            continue
            
        duration = (last_move_at - created_at) // 1000
        durations.append(duration)
    if len(durations) == 0:
        return 0
    return sum(durations)//len(durations)
    
            
#--------------------------------------------------------------------------------------------#

def get_game_data(username):
    response = get_game_json(username)
    if response == None: 
        return None
    elif response.status_code == 429:
        return "rate_limited"
    
    response_lines = [line.decode("utf-8") for line in response.iter_lines() if line]
    
    top_eco, second_eco, top_winrate_eco, second_winrate_eco = get_ECO_data(response_lines, username)
    
    white_win_rate, white_lose_rate, white_draw_rate, white_game_count, black_win_rate, black_lose_rate, black_draw_rate, black_game_count = get_color_specific_winrates(response_lines, username)
    
    mate_winrate, resign_winrate, time_winrate, mate_lossrate, resign_lossrate, time_lossrate = get_gameEnd_data(response_lines, username)
    
    average_game_len= get_game_lengths(response_lines)
    
    return {
        "status": "success",
        "white_win_rate": white_win_rate,
        "white_lose_rate": white_lose_rate,
        "white_draw_rate": white_draw_rate,
        "white_game_count": white_game_count,
        "black_win_rate": black_win_rate,
        "black_lose_rate": black_lose_rate,
        "black_draw_rate": black_draw_rate,
        "black_game_count": black_game_count,
        "top_eco": top_eco,
        "second_eco": second_eco,
        "top_winrate_eco": top_winrate_eco,
        "second_winrate_eco": second_winrate_eco,
        "mate_winrate": mate_winrate,
        "resign_winrate": resign_winrate,
        "time_winrate": time_winrate,
        "mate_lossrate": mate_lossrate,
        "resign_lossrate": resign_lossrate,
        "time_lossrate": time_lossrate,
        "average_game_len": average_game_len
    }
    
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
        game_data = get_game_data(username)
        
        if game_data is None:
            print(f"Skipping user {username} due to fetch error.")
            df.at[index, 'white_win_rate'] = 0
            df.at[index, 'white_lose_rate'] = 0
            df.at[index, 'white_draw_rate'] = 0
            df.at[index, 'white_game_count'] = 0
            df.at[index, 'black_win_rate'] = 0
            df.at[index, 'black_lose_rate'] = 0
            df.at[index, 'black_draw_rate'] = 0
            df.at[index, 'black_game_count'] = 0
            df.at[index, 'top_eco'] = None
            df.at[index, 'second_eco'] = None
            df.at[index, 'top_winrate_eco'] = None
            df.at[index, 'second_winrate_eco'] = None
            df.at[index, 'mate_winrate'] = 0
            df.at[index, 'resign_winrate'] = 0
            df.at[index, 'time_winrate'] = 0
            df.at[index, 'mate_lossrate'] = 0
            df.at[index, 'resign_lossrate'] = 0
            df.at[index, "time_lossrate"] = 0
            df.at[index, "average_game_len"] = 0
            continue
        elif game_data == "rate_limited":
            print("Rate limit reached. Saving progress and pausing.")
            save_progress(df)
            time.sleep(120)
            continue
        df.at[index, 'white_win_rate'] = game_data["white_win_rate"]
        df.at[index, 'white_lose_rate'] = game_data["white_lose_rate"]
        df.at[index, 'white_draw_rate'] = game_data["white_draw_rate"]
        df.at[index, 'white_game_count'] = game_data["white_game_count"]
        df.at[index, 'black_win_rate'] = game_data["black_win_rate"]
        df.at[index, 'black_lose_rate'] = game_data["black_lose_rate"]
        df.at[index, 'black_draw_rate'] = game_data["black_draw_rate"]
        df.at[index, 'black_game_count'] = game_data["black_game_count"]
        df.at[index, 'top_eco'] = game_data["top_eco"]
        df.at[index, 'second_eco'] = game_data["second_eco"]
        df.at[index, 'top_winrate_eco'] = game_data["top_winrate_eco"]
        df.at[index, 'second_winrate_eco'] = game_data["second_winrate_eco"]
        df.at[index, 'mate_winrate'] = game_data["mate_winrate"]
        df.at[index, 'resign_winrate'] = game_data["resign_winrate"]
        df.at[index, 'time_winrate'] = game_data["time_winrate"]
        df.at[index, 'mate_lossrate'] = game_data["mate_lossrate"]
        df.at[index, 'resign_lossrate'] = game_data["resign_lossrate"]
        df.at[index, "time_lossrate"] = game_data["time_lossrate"]
        df.at[index, "average_game_len"] = game_data["average_game_len"]

        print(f"Processed user {username}. Saving progress...")
        save_progress(df)
    return df

#--------------------------------------------------------------------------------------------#

# Run the function and save the results to a new CSV file
df, _ = load_progress()
df = add_user_stats(df)
df.to_csv('final.csv', index=False)
