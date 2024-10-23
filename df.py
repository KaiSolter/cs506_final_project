import requests
import pandas as pd
import json

def get_user_ids_from_public_games(number_of_ids=50):
    user_ids = set()  # Use a set to ensure no duplicate user IDs
    headers = {"Accept": "application/x-ndjson"}

    # Sample users to get some games
    sample_users = ["lichess", "ChessNetwork", "EricRosen", "agadmator"]

    for user in sample_users:
        url = f"https://lichess.org/api/games/user/{user}"
        
        # Request the user's public games
        response = requests.get(url, headers=headers, params={"max": 15}, stream=True)

        if response.status_code != 200:
            print(f"Error while fetching data for user {user}: {response.status_code}")
            continue

        # Iterate over each game line and extract usernames
        for line in response.iter_lines():
            if line:
                game_data = json.loads(line.decode('utf-8'))

                # Add the usernames of white and black players
                if "players" in game_data:
                    white_player = game_data["players"].get("white", {}).get("user", {}).get("name")
                    black_player = game_data["players"].get("black", {}).get("user", {}).get("name")

                    if white_player:
                        user_ids.add(white_player)
                    if black_player:
                        user_ids.add(black_player)

                # Stop when we reach the desired number of user IDs
                if len(user_ids) >= number_of_ids:
                    break

        # Break the loop if we have enough user IDs
        if len(user_ids) >= number_of_ids:
            break

    return list(user_ids)

# Get a list of user IDs
user_ids_list = get_user_ids_from_public_games(50)

# Create a DataFrame with the user IDs
df = pd.DataFrame(user_ids_list, columns=['User ID'])

print(df)
