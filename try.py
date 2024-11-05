import requests
import json
import pandas as pd

df = pd.read_csv('normalized1.csv')

# Rate limit logic, save current progress
def save_progress(results_df):
    """Saves the results DataFrame to progress.csv."""
    results_df.to_csv('progress.csv', index=False)
    print("Progress saved to progress.csv")

# Rate limit logic, continue from last user id
def load_progress():
    """Loads progress from progress.csv and identifies the last user processed."""
    try:
        results_df = pd.read_csv('progress.csv')
        last_user_processed = results_df['user_id'].iloc[-1]
        print(f"Resuming from user ID: {last_user_processed}")
        return results_df, last_user_processed
    except FileNotFoundError:
        print("No progress file found. Starting from scratch.")
        columns = ['user_id', 'win_rate', 'lose_rate', 'draw_rate', 'game_count']
        results_df = pd.DataFrame(columns=columns)
        return results_df, None

def get_win_rate(username):
    url = f"https://lichess.org/api/games/user/{username}"
    params = {
        "max": 100,
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
        return "rate_limited", None, None, None, 0
    if response.status_code != 200:
        print(f"Failed to fetch data for {username}. Ensure the username is correct.")
        return None, None, None, None, 0

    win_count = 0
    draw_count = 0
    loss_count = 0
    game_count = 0

    for line in response.iter_lines():
        if line:
            game = line.decode("utf-8")
            game_data = json.loads(game)
            
            # Only consider games where the user is the black player
            if ("user" in game_data["players"]["black"] and
                game_data["players"]["black"]["user"]["name"].lower() == username.lower()):
                if "winner" in game_data:
                    if game_data["winner"] == "black":
                        win_count += 1
                    else:
                        loss_count += 1
                else:
                    draw_count += 1  # No winner field means it was a draw
                game_count += 1

    if game_count == 0:
        print(f"No blitz games found for user: {username} as black.")
        return "success", 0.0, 0.0, 0.0, 0

    win_rate = (win_count / game_count) * 100
    lose_rate = (loss_count / game_count) * 100
    draw_rate = (draw_count / game_count) * 100
    print(f"Win Rate for {username} as Black in Blitz: {win_rate:.2f}%")
    print(f"Lose Rate for {username} as Black in Blitz: {lose_rate:.2f}%") 
    print(f"Draw Rate for {username} as Black in Blitz: {draw_rate:.2f}%")
    print(f"Wins: {win_count}, Draws: {draw_count}, Losses: {loss_count}, Total Blitz Games as Black: {game_count}")
    return "success", win_rate, lose_rate, draw_rate, game_count

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
        status, win_rate, lose_rate, draw_rate, game_count = get_win_rate(username)
        
        if status == "rate_limited":
            save_progress(results_df)
            break
        elif status == "success":
            user_stats = {
                'user_id': username,
                'win_rate': win_rate,
                'lose_rate': lose_rate,
                'draw_rate': draw_rate,
                'game_count': game_count
            }
            results_df = pd.concat([results_df, pd.DataFrame([user_stats])], ignore_index=True)
        else:
            print(f"Skipping user {username} due to fetch error.")
            user_stats = {
                'user_id': username,
                'win_rate': None,
                'lose_rate': None,
                'draw_rate': None,
                'game_count': None
            }
            results_df = pd.concat([results_df, pd.DataFrame([user_stats])], ignore_index=True)
            save_progress(results_df)


    return results_df

# Run the function and save the results to a new CSV file
results_df = add_user_stats(df)
results_df.to_csv('stats.csv', index=False)
print("Results saved to stats.csv")
