import requests
import pandas as pd
import json
import time
import random
import os

total_ids = set() #total dataframe of every user id collected
count = 1 #global counter for an exponential backoff

if os.path.exists("progress_0.csv"):
    os.remove("progress_0.csv")
    print("progress_0.csv deleted.")
else:
    print("No existing progress_0.csv found.")

df = pd.read_csv('deviation_stats_2nd.csv')

def save_progress(total_ids, current_ids):
    """Saves the DataFrame to progress_0.csv."""
    total_ids.update(current_ids)
    df = pd.DataFrame({'user_id': list(total_ids)})
    df.to_csv('progress_0.csv', index=False)
    print("Progress saved to progress_0.csv")

headers = {"Accept": "application/x-ndjson"} 

def getnops(n, username, user_ids): 
    global count
    global total_ids
    startinglen = len(user_ids)
    url = "https://lichess.org/api/games/user/" + username
    try:
        print('Requesting data for:', username)
        response = requests.get(url, headers=headers, params={"max": n}, stream=True, timeout=10)  # Increase timeout to 10 seconds
        if response.status_code == 429:
            print(f"Rate limited. Waiting {30 + 2**count} seconds...")
            time.sleep(30 + 2**count) 
            return
        elif response.status_code != 200:
            count = count + .5
            save_progress(total_ids, current_user_ids )
            print(f"Error while fetching data for user {username}: {response.status_code} saving progress")
            return
    except requests.exceptions.ConnectTimeout:
        save_progress(total_ids, current_user_ids )
        print(f"Connection to {url} timed out. Skipping this user.")
        return
    except requests.exceptions.RequestException as e:
        save_progress(total_ids, current_user_ids )
        print(f"An error occurred: {e}")
        return

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

                if white_player:
                    user_ids.add(white_player)
                if black_player:
                    user_ids.add(black_player)

            # Stop when we reach the desired number of user IDs
            if len(user_ids) >= startinglen + n:
                break

STARTING_USERS = ["winx_m", "GK1963", "hungzhao", "Iwantogotoswizerland", "Gatotkoco995", "sergiosf97", "khairinasir",
                  "TrentAllgood", "kitikita123", "wcarmona", "Josue_Daza", "Gennadiy300iq", "mzauber", "DruzhkovVN", 
                  "Sys87", "pichibart"]

for user in STARTING_USERS:
    current_user_ids = set() #collected user ids 
    used_ids = set() #user ids used for collection
    current_user_ids.add(user)
    for i in range(1, 1200):
        available_ids = list(current_user_ids - used_ids)
        if(available_ids):
            searchUser = random.choice(available_ids)
        else: 
            continue
        print("Fetching games for:", searchUser)
        getnops(15, searchUser, current_user_ids)
        time.sleep(1)
        print("Fetched games for:", searchUser)
        used_ids.add(searchUser)
    total_ids.update(current_user_ids)

df = pd.DataFrame({'user_id': list(total_ids)})
df.to_csv('fullDataset_0.csv', index=False)