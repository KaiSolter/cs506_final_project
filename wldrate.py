import requests
import json  # Import json to handle JSON parsing
import pandas as pd

df = pd.read_csv('normalized1.csv')

#fetch blitz games only


#rate limit logic, save current progress
def save_progress(df):
    """Saves the DataFrame to progress.csv."""
    df.to_csv('progress.csv', index=False)
    print("Progress saved to progress.csv")

#rate limit logic, continue from last user id
def load_progress(df):
    """Loads progress from progress.csv and identifies the last user processed."""
    try:
        progress_df = pd.read_csv('progress.csv')
        last_user_processed = progress_df['user_id'].iloc[-1]
        print(f"Resuming from user ID: {last_user_processed}")
        return progress_df, last_user_processed
    except FileNotFoundError:
        print("No progress file found. Starting from scratch.")
        return df, None

def get_win_rate(username):
    # API endpoint to fetch up to 100 recent games
    url = f"https://lichess.org/api/games/user/{username}"
    params = {
        "max": 100,
        "opening": False,
        "clocks": False,
        "evals": False,
        "pgnInJson": True,  # Enable JSON format for easier parsing
    }
    
    # Request headers to avoid rate limiting
    headers = {
        "Accept": "application/x-ndjson",
        "User-Agent": "WinRateCalculator/1.0"  # Custom user-agent for identification
    }

    response = requests.get(url, params=params, headers=headers, stream=True)
    if response.status_code == 429:  # Rate limit hit
        print("Rate limit hit. Stopping process and saving progress.")
        return "rate_limited", None, None, None, 0
    if response.status_code != 200:
        print("Failed to fetch data. Ensure the username is correct.")
        return None, None, None, None, 0

    win_count = 0
    draw_count = 0
    loss_count = 0
    game_count = 0

    # Parse the NDJSON response line by line
    for line in response.iter_lines():
        if line:
            game = line.decode("utf-8")
            game_data = json.loads(game)  
            
            # Determine if the user won, lost, or drew
            if "winner" in game_data:
                # Check if the user is the white player and won
                if ("user" in game_data["players"]["white"] and
                    game_data["players"]["white"]["user"]["name"].lower() == username.lower()):
                    if game_data["winner"] == "white":
                        win_count += 1
                    else:
                        loss_count += 1
                # Check if the user is the black player and won
                elif ("user" in game_data["players"]["black"] and
                      game_data["players"]["black"]["user"]["name"].lower() == username.lower()):
                    if game_data["winner"] == "black":
                        win_count += 1
                    else:
                        loss_count += 1
                else:
                    # Game is a loss if user is not found as winner
                    loss_count += 1
            else:
                draw_count += 1  # No winner field means it was a draw

            game_count += 1

    # Calculate win rate
    if game_count == 0:
        print("No games found for this user.")
        return 0.0, 0.0, 0.0, 0

    win_rate = (win_count / game_count) * 100
    lose_rate = (loss_count / game_count) * 100
    draw_rate = (draw_count / game_count) * 100
    print(f"Win Rate for {username}: {win_rate:.2f}%")
    print(f"Lose Rate for {username}: {lose_rate:.2f}%") 
    print(f"Draw Rate for {username}: {draw_rate:.2f}%")
    print(f"Wins: {win_count}, Draws: {draw_count}, Losses: {loss_count}, Total Games: {game_count}")
    return "success", win_rate, lose_rate, draw_rate, game_count


# Example usage
# get_win_rate("Lose2U")

def add_user_stats(df):
    df, last_user_processed = load_progress(df)
    start_index = 0
    if last_user_processed:
        start_index = df[df['user_id'] == last_user_processed].index[0] + 1
        
    # Create empty columns for the stats
    for col in ['win_rate', 'lose_rate', 'draw_rate', 'game_count']:
        if col not in df.columns:
            df['win_rate'] = 0.0
            df['lose_rate'] = 0.0
            df['draw_rate'] = 0.0
            df['game_count'] = 0

    for index, row in df.iloc[start_index:].iterrows():
        status, win_rate, lose_rate, draw_rate, game_count = get_win_rate(row['user_id'])
        
        if status == "rate_limited":
            # Save progress and stop if rate limit is hit
            save_progress(df)
            break
        elif win_rate is not None:  # Update the row with fetched data if successful
            df.at[index, 'win_rate'] = win_rate
            df.at[index, 'lose_rate'] = lose_rate
            df.at[index, 'draw_rate'] = draw_rate
            df.at[index, 'game_count'] = game_count

    return df


df = add_user_stats(df)
df.to_csv('stats.csv', index = False)
