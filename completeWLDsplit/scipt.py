import pandas as pd


df = pd.read_csv('save2.csv')

df = df.drop_duplicates(subset=['user_id'])

df.to_csv('save2.csv', index=False)