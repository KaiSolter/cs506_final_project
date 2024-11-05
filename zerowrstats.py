import requests
import json  # Import json to handle JSON parsing
import pandas as pd

df = pd.read_csv('final_stats.csv')

# new_df = df[df['game_count'] == 0].copy()

# new_df.to_csv('nullcsv.csv', index=False)

df = df[df['game_count'] != 0].reset_index(drop=True)

df.to_csv('blitz_players.csv', index = False)

