import pandas as pd

df = pd.read_csv("1full.csv")

df = df.dropna()
df = df.drop_duplicates(subset=['user_id'])
df = df[df['blitz_rating'] != 0]

df.to_csv('1full.csv', index=False)
