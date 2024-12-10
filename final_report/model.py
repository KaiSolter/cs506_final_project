import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score




df = pd.read_csv('final_report/FINAL.csv', header= 0)
df = df.dropna()


game_counts = [
   'user_game_count',
   'op_game_count',
   'user_blitz_total_games',
   'op_blitz_total_games'
]
for column in game_counts:
   df = df[df[column] >= 10]


game_0s = [
   'user_win_rate',
   'user_lose_rate',
   'user_mate_winrate',
   'user_mate_lossrate',
   'op_win_rate',
   'op_lose_rate',
   'op_mate_winrate',
   'op_mate_lossrate',
   'op_blitz_rating'
 
]
for column in game_0s:
   df = df[df[column] != 0]






columns_to_encode = ['user_top_eco', 'user_second_eco', 'user_top_winrate_eco', 'user_second_winrate_eco', 'op_top_eco', 'op_second_eco', 'op_top_winrate_eco', 'op_second_winrate_eco']
# Initialize the label encoder
label_encoders = {}




# Perform label encoding
for column in columns_to_encode:
   label_encoders[column] = LabelEncoder()
   df[column] = label_encoders[column].fit_transform(df[column])


df['op_average_best_win'] = df[['op_best_win_1', 'op_best_win_2', 'op_best_win_3']].mean(axis=1)
df['user_average_best_win'] = df[['user_best_win_1', 'user_best_win_2', 'user_best_win_3']].mean(axis=1)
df['best_win_diff'] = df['user_best_win_1'] - df['op_best_win_1']
df['user_lose_len'] = df['user_time_lossrate'] / df['op_average_game_len']
df['op_lose_len'] = df['op_time_lossrate'] / df['user_average_game_len']
df['user_white_performance'] = df['user_white_win_rate'] * (df['op_black_lose_rate'])
df['user_black_performance'] = df['user_black_win_rate'] * (df['op_white_lose_rate'])
df['op_white_performance'] = df['op_white_win_rate'] * (df['user_black_lose_rate'])
df['op_black_performance'] = df['op_black_win_rate'] * (df['user_white_lose_rate'])
df['combined_draw4'] = (df['user_white_draw_rate'] + df['op_black_draw_rate'] + df['user_black_draw_rate'] + df['op_white_draw_rate'])/4
df['user_time_performance'] = df['user_time_winrate'] * df['op_time_lossrate']


df['op_time_performance'] = df['op_time_winrate'] * df['user_time_lossrate']
df['user_performace'] = df['user_win_rate'] * (df['op_lose_rate'])
df['op_performance'] = df['op_win_rate'] * (df['user_lose_rate'])
df['rating_diff'] = df['user_blitz_rating'] - df['op_blitz_rating']
df['user_resign_perf'] = (df['user_resign_winrate'] * df['op_resign_lossrate'])
df['op_resign_perf'] = (df['op_resign_winrate'] * df['user_resign_lossrate'])
df['game_count_ratio'] = df['user_game_count'] / df['op_game_count']
df['user_mate_perf'] = df['user_mate_winrate'] * df['op_mate_lossrate']
df['op_mate_perf'] = df['op_mate_winrate'] * df['user_mate_lossrate']
df['deviation_compare'] = df['user_rating_deviation'] / df['op_rating_deviation']
df['compare_len'] = df['user_average_game_len'] / df['op_average_game_len']






remove = [
   # 'user_id','op_id',
   'user_rating_bin', 'user_top_eco',
      'user_second_eco', 'user_top_winrate_eco', 'user_second_winrate_eco', 'op_top_eco',
      'op_second_eco', 'op_top_winrate_eco', 'op_second_winrate_eco', 'user_best_win_1','user_best_win_2', 'user_best_win_3',
      'op_best_win_1', 'op_best_win_2', 'op_best_win_3', 'user_white_win_rate', 'op_black_lose_rate', 'user_black_win_rate',
      'op_white_lose_rate', 'op_white_win_rate', 'user_black_lose_rate', 'op_black_win_rate', 'user_white_lose_rate',
      'user_win_rate', 'user_lose_rate', 'op_win_rate', 'op_lose_rate', 'user_blitz_rating', 'op_blitz_rating',
      #'high_draw_rate',
      'op_black_game_count','user_black_game_count','op_white_game_count', 'user_white_game_count',
      'user_blitz_total_games', 'op_blitz_total_games',
      'op_game_count', 'user_game_count', #tried
      'op_draw_rate', 'user_draw_rate', 'op_time_lossrate', 'user_time_lossrate',
      'op_mate_winrate', 'user_mate_winrate', 'op_white_draw_rate', 'op_black_draw_rate', 'user_white_draw_rate', 'user_black_draw_rate',
     #  'user_time_performance', 'op_time_performance',
     'op_average_game_len', 'user_average_game_len',
      'op_mate_lossrate', 'user_mate_lossrate',
       'op_resign_lossrate', 'user_resign_lossrate',
       'op_resign_winrate', 'user_resign_winrate'
     
]


df = df.drop(columns=remove)
df.to_csv('final_report/cleanedData.csv', index = False)




data = pd.read_csv('final_report/cleanedData.csv')


X = data.drop(columns=['game_result', 'user_id', 'op_id'])
y = data['game_result']


# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)


# Train the Random Forest model with predefined parameters
rf = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42)
rf.fit(X_train, y_train)


# Make predictions
y_pred = rf.predict(X_test)


# Evaluate accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy with Selected Parameters:", accuracy)


