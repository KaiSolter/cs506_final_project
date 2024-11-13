import csv
import requests
import time
import json


def get_losses_by_time(user_id):
    url = f"https://lichess.org/api/games/user/{user_id}"
    params = {
        'max': 100,           # maximum number of games to fetch
        'perfType': 'blitz',  # filter by game type (can be removed or modified if needed)
        'analysed': False,
        'sort': 'date',
        'moves': False,
        'pgnInJson': True
    }
    
    headers = {
        'Accept': 'application/x-ndjson'
    }
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching games for {user_id}. Status code: {response.status_code}")
        return None

    losses_by_time = 0
    games = response.text.strip().splitlines()
    
    for game_data in games:
        game = json.loads(game_data)
        # Check if the game ended due to time and has a 'winner'
        if game.get('status') == 'outoftime' and 'winner' in game:
            # Ensure 'players' and 'white' keys exist, and 'user' info is available
            if 'players' in game and 'white' in game['players'] and 'user' in game['players']['white']:
                # Check if the winner was not the user (indicating loss by time)
                if game['winner'] != game['players']['white']['user']['name']:
                    losses_by_time += 1
    
    return losses_by_time

    
def main():
    input_file = "past_csv/sample1.csv"
    output_file = "output.csv"

    with open(input_file, mode='r') as infile, open(output_file, mode='w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['user_id', 'losses_by_time']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            user_id = row['user_id']
            print(f"Processing {user_id}")
            losses_by_time = get_losses_by_time(user_id)
            if losses_by_time is not None:
                writer.writerow({'user_id': user_id, 'losses_by_time': losses_by_time})
            time.sleep(1)  # To avoid hitting API rate limits

if __name__ == "__main__":
    main()
