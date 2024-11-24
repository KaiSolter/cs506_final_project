import requests
import json  # Import json to handle JSON parsing
import pandas as pd

df = pd.read_csv('split2p3.csv')

#----------------------------------------------------------------------------------#
#fetch blitz games only

def fetch_blitz_games(username, max_blitz_games=100, max_total_games=300):
    url = f"https://lichess.org/api/games/user/{username}"
    headers = {
        "Accept": "application/x-ndjson",
        "User-Agent": "BlitzGameFetcher/1.0"
    }
    win_count = 0
    draw_count = 0
    loss_count = 0
    blitz_game_count = 0
    total_games_checked = 0
    batch_size = 100
    timeout = 20  # Set a timeout of 10 seconds

    while blitz_game_count < max_blitz_games and total_games_checked < max_total_games:
        params = {
            "max": batch_size,
            "opening": False,
            "clocks": False,
            "evals": False,
            "pgnInJson": True
        }

        try:
            response = requests.get(url, params=params, headers=headers, stream=True, timeout=timeout)
            if response.status_code == 429:
                print("Rate limit hit. Stopping fetch to avoid further requests.")
                return {
                    "status": "rate_limited",
                    "win_count": win_count,
                    "loss_count": loss_count,
                    "draw_count": draw_count,
                    "blitz_game_count": blitz_game_count,
                    "total_games_checked": total_games_checked
                }

            elif response.status_code != 200:
                print(f"Failed to retrieve data for {username}. Status code: {response.status_code}")
                return {"status": "failed"}

            games_in_batch = 0
            for line in response.iter_lines():
                if line:
                    game_data = json.loads(line.decode("utf-8"))
                    total_games_checked += 1
                    games_in_batch += 1

                    if game_data.get("speed") == "blitz":
                        blitz_game_count += 1
                        if "winner" in game_data:
                            if (game_data["players"]["white"].get("user", {}).get("name", "").lower() == username.lower() and game_data["winner"] == "white") or \
                               (game_data["players"]["black"].get("user", {}).get("name", "").lower() == username.lower() and game_data["winner"] == "black"):
                                win_count += 1
                            else:
                                loss_count += 1
                        else:
                            draw_count += 1

                    if blitz_game_count >= max_blitz_games or total_games_checked >= max_total_games:
                        break

            # If the batch contains fewer games than requested, we likely reached the end of available games.
            if games_in_batch < batch_size:
                print(f"Reached end of available games for {username}. Total games checked: {total_games_checked}")
                break

        except requests.exceptions.ConnectTimeout:
            print(f"Timeout error for user {username}. Retrying...")
            continue

        except requests.exceptions.RequestException as e:
            print(f"An error occurred for user {username}: {e}")
            return {"status": "failed"}

    return {
        "status": "success",
        "win_count": win_count,
        "loss_count": loss_count,
        "draw_count": draw_count,
        "blitz_game_count": blitz_game_count,
        "total_games_checked": total_games_checked
    }

    
#------------------------------------------------------------------------------------#
#rate limit logic

#save current progress
def save_progress(df):
    """Saves the DataFrame to progress.csv."""
    df.to_csv('split2progress3.csv', index=False)
    print("Progress saved to progress.csv")

#continue from last user id
def load_progress():
    """Loads progress from progress.csv and identifies the last user processed."""
    try:
        progress_df = pd.read_csv('split2progress3.csv')
        last_user_processed = progress_df['user_id'].iloc[-1]
        print(f"Resuming from user ID: {last_user_processed}")
        return progress_df, last_user_processed
    except FileNotFoundError:
        print("No progress file found. Starting from scratch.")
        return pd.read_csv('split2p3.csv'), None
    
    
#--------------------------------------------------------------------------------------------#
#calculating the winrate of what is being passed in

def get_win_rate(username):
    result = fetch_blitz_games(username)
    if result["status"] == "rate_limited":
        print("Rate limit encountered. Implement custom rate limit handling logic here.")
        return "rate_limited", None, None, None, 0
    elif result["status"] == "failed":
        return "failed", None, None, None, 0

    blitz_game_count = result["blitz_game_count"]
    if blitz_game_count == 0:
        print("No Blitz games found for this user.")
        return "no_games", 0, 0, 0, 0  # Return integer zeroes if no games

    # Calculate win, loss, and draw rates as integer percentages
    win_rate = int((result["win_count"] / blitz_game_count) * 100)
    lose_rate = int((result["loss_count"] / blitz_game_count) * 100)
    draw_rate = int((result["draw_count"] / blitz_game_count) * 100)

    print(f"Blitz Win Rate for {username}: {win_rate}%")
    print(f"Blitz Lose Rate for {username}: {lose_rate}%")
    print(f"Blitz Draw Rate for {username}: {draw_rate}%")
    print(f"Total Blitz Games: {blitz_game_count} out of {result['total_games_checked']} games checked")

    return "success", win_rate, lose_rate, draw_rate, blitz_game_count


# Example usage
# get_win_rate("Lose2U")

#--------------------------------------------------------------------------------------------------------#
#add winrate of user

def add_user_stats(df):

    start_index = 0
    df, last_user_processed = load_progress()
    if last_user_processed:
        start_index = df[df['user_id'] == last_user_processed].index[0] + 1
        
    # Create empty columns for the stats
    for col in ['win_rate', 'lose_rate', 'draw_rate', 'game_count']:
        if col not in df.columns:
            df[col] = 0.0

    while start_index < len(df):
        row = df.iloc[start_index]
        user_id = row['user_id']
        status, win_rate, lose_rate, draw_rate, game_count = get_win_rate(user_id)

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
            df.at[start_index, 'win_rate'] = win_rate
            df.at[start_index, 'lose_rate'] = lose_rate
            df.at[start_index, 'draw_rate'] = draw_rate
            df.at[start_index, 'game_count'] = game_count

        # Save progress after each user and move to the next
        save_progress(df)
        start_index += 1

    # Final save to ensure all progress is written
    df.to_csv('split2wldr3.csv', index=False)
    print("All users processed and final stats saved to final_stats.csv")
    
    return df

# Assuming get_win_rate and fetch_blitz_games functions are defined as in previous instructions
df, _ = load_progress()
df = add_user_stats(df)

