import requests
import pandas as pd
import json
import time
import random

API_BASE_URL = "https://lichess.org/api/games/user/"
total_ids = set() #total dataframe of every user id collected
STARTING_USERS = ["winx_m", "GK1963", "hungzhao", "Iwantogotoswizerland", "Gatotkoco995", "sergiosf97", "khairinasir",
                  "TrentAllgood", "kitikita123", "wcarmona", "Josue_Daza", "Gennadiy300iq", "mzauber", "DruzhkovVN", 
                  "Sys87", "pichibart"]
num_ids = 100
headers = {"Accept": "application/x-ndjson"} 


def getnops(n, username, user_ids): 
    startinglen = len(user_ids)
    url = API_BASE_URL + username
    try:
        response = requests.get(url, headers=headers, params={"max": n}, stream=True, timeout=10)  # Increase timeout to 10 seconds
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 4)
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
    for i in range(1, 150): 
        available_ids = list(current_user_ids - used_ids)
        if(available_ids):
            searchUser = random.choice(available_ids)
        else: 
            continue
        print("Fetching games for:", searchUser)
        getnops(15, searchUser, current_user_ids)
        print("Fetched games for:", searchUser)
        used_ids.add(searchUser)
    total_ids.update(current_user_ids)
df = pd.DataFrame({'user_id': list(total_ids)})

rating_list = []

def fetch_user_rating(user_id):
    url = f"https://lichess.org/api/user/{user_id}"
    headers = {
        'Accept': 'application/json',
        # 'Authorization': 'Bearer YOUR_API_TOKEN'  # Optional: Include if you have an API token
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 429:
            print(f"Rate limited. Waiting {4} seconds...")
            time.sleep(4)
            return
        response.raise_for_status()
        data = response.json()
        
        blitz = data.get('perfs', {}).get('blitz', {})
        rating = blitz.get('rating', None)
        
        return rating
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error for {user_id}: {http_err}")

for user in list(total_ids):
    rating =fetch_user_rating(user)
    print("rating for",user, "is",rating)
    rating_list.append(rating)


df['blitz_rating'] = rating_list
df.to_csv('lichess_user_ratings.csv', index=False)


print("printing df here")
print(df)
print(df.shape)
