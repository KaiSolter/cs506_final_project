import requests
import pandas as pd
import json
import time
import random

API_BASE_URL = "https://lichess.org/api/games/user/"
total_ids = set() #total dataframe of every user id collected
STARTING_USERS = ["winx_m", "GK1963", "hungzhao", "Iwantogotoswizerland", "Gatotkoco995", "sergiosf97", "khairinasi",
                  "TrentAllgood", "kitikita123", "wcarmona", "Josue_Daza", "Gennadiy300iq", "mzauber", "DruzhkovVN", 
                  "Sys87", "pichibart"]
num_ids = 100
headers = {"Accept": "application/x-ndjson"} 


def getnops(n, username): 
    startinglen = len(user_ids)
    url = API_BASE_URL + username
    try:
        response = requests.get(url, headers=headers, params={"max": n}, stream=True, timeout=10)  # Increase timeout to 10 seconds
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 5)
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(int(retry_after))
            return
        elif response.status_code != 200:
            print(f"Error while fetching data for user {username}: {response.status_code}")
            return
    except requests.exceptions.ConnectTimeout:
        print(f"Connection to {url} timed out. Skipping this user.")
        return
    except requests.exceptions.RequestException as e:
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


for user in STARTING_USERS:
    current_user_ids = set() #collected user ids 
    used_ids = set() #user ids used for collection
    current_user_ids.add(user)
    for i in range(1, 1000): 
        while(True):
            searchUser = random.choice(list(current_user_ids))
            if(searchUser not in used_ids):
                break
        print("Fetching games for:", searchUser)
        getnops(15, searchUser)
        print("Fetched games for:", searchUser)
        used_ids.add(searchUser)
    total_ids.update(current_user_ids)
df = pd.DataFrame(total_ids, columns=['User ID'])


# for i in range(1, 1000): 
#     while(True):
#         searchUser = random.choice(list(user_ids))
#         if(searchUser not in used_ids):
#             break
#     print("Fetching games for:", searchUser)
#     getnops(15, searchUser)
#     print("Fetched games for:", searchUser)
#     used_ids.add(searchUser)



print(df)