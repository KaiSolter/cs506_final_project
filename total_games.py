import requests
import pandas as pd

def get_total_games_played(username):
    """
    Fetches the total number of games played by a Lichess user.
    
    Parameters:
        username (str): The Lichess username to fetch data for.
    
    Returns:
        int: Total games played by the user, or -1 if the request fails.
    """
    url = f"https://lichess.org/api/user/{username}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            user_data = response.json()
            blitz_games = user_data.get('perfs', {}).get('blitz', {}).get('games', 0)
            print(f"Blitz games played by {username}: {blitz_games}")
            return blitz_games
        else:
            print(f"Failed to retrieve data for {username}. Status code: {response.status_code}")
            return -1
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return -1

def get_blitz_games(df): 
    total_blitz = []
    for user in df['user_id']:
        blitz_games = get_total_games_played(user)
        total_blitz.append(blitz_games)
    df['total_games_played'] = total_blitz
    return df

df = pd.read_csv('normalized1.csv')
new_df = get_blitz_games(df)
df.to_csv('with_total_games.csv')
