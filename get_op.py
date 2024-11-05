import requests
import pandas as pd
import json
import time

headers = {"Accept": "application/x-ndjson"} 

def get_recent_op(username): 
    url = "https://lichess.org/api/games/user/" + username
    try:
        response = requests.get(url, headers=headers, params={"max": 1}, stream=True, timeout=10)  
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

                if white_player == username: 
                    op = black_player
                    if game_data["winner"] == "white":
                        score = 1
                    elif game_data["winner"] == "black":
                        score = -1
                    else:
                        score = 0
                elif black_player == username:
                    op = white_player
                    if game_data["winner"] == "white":
                        score = -1
                    elif game_data["winner"] == "black":
                        score = 1
                    else:
                        score = 0
            return op, score
        
print(get_recent_op("KaiSolter"))