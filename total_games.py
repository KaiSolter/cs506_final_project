import requests

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
            total_games = user_data.get('count', {}).get('all', 0)
            print(f"Total games played by {username}: {total_games}")
            return total_games
        else:
            print(f"Failed to retrieve data for {username}. Status code: {response.status_code}")
            return -1
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return -1

# Example usage
# total_games = get_total_games_played("exampleUser")
# print(total_games)
