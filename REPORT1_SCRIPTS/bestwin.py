import requests
import pandas as pd

def fetch_highest_blitz_rated_opponent(df):
    # Initialize lists to store the ratings
    highest_ratings = []
    second_highest_ratings = []
    third_highest_ratings = []
    
    for user in df['user_id']:
        print('fetching best wins for: ', user)
        try:
            # Endpoint to fetch blitz performance data for the user
            url = f'https://lichess.org/api/user/{user}/perf/blitz'
            headers = {'Accept': 'application/json'}
            
            response = requests.get(url, headers=headers)

            # Check if the request was successful and the response is JSON
            if response.status_code == 200:
                data = response.json()
                best_wins = data.get("stat", {}).get("bestWins", {})
                if best_wins and 'results' in best_wins and len(best_wins['results']) >= 3:
                    # Extract top three opponent ratings
                    highest_ratings.append(best_wins['results'][0]['opRating'])
                    second_highest_ratings.append(best_wins['results'][1]['opRating'])
                    third_highest_ratings.append(best_wins['results'][2]['opRating'])
                else:
                    # Append NaN if data is insufficient
                    highest_ratings.append(None)
                    second_highest_ratings.append(None)
                    third_highest_ratings.append(None)
            else:
                print(f"Failed to fetch blitz data for user {user}. Status code: {response.status_code}")
                highest_ratings.append(None)
                second_highest_ratings.append(None)
                third_highest_ratings.append(None)

        except Exception as e:
            print(f"Error fetching data for user {user}: {e}")
            # Append NaN in case of any exception
            highest_ratings.append(None)
            second_highest_ratings.append(None)
            third_highest_ratings.append(None)

    # Add new columns to the DataFrame
    df['highest_blitz_opponent_rating'] = highest_ratings
    df['second_highest_blitz_opponent_rating'] = second_highest_ratings
    df['third_highest_blitz_opponent_rating'] = third_highest_ratings
    
    return df
df = pd.read_csv('normalized1.csv')
new_df = fetch_highest_blitz_rated_opponent(df)
new_df.to_csv('withblitzrating.csv', index=False)
