import requests
import pandas as pd

def fetch_streaks_for_user(user):
    print('Fetching winstreak for:', user)
    try:
        url = f'https://lichess.org/api/user/{user}/perf/blitz'
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            result_streak = data.get("stat", {}).get("resultStreak", {})
            
            win_streak_cur = result_streak.get('win', {}).get('cur', {}).get('v', 0)
            win_streak_max = result_streak.get('win', {}).get('max', {}).get('v', 0)
            loss_streak_cur = result_streak.get('loss', {}).get('cur', {}).get('v', 0)
            loss_streak_max = result_streak.get('loss', {}).get('max', {}).get('v', 0)
            
            print("Win streak max:", win_streak_max)
            print("Win streak cur:", win_streak_cur)
            print("Loss streak max:", loss_streak_max)
            print("Loss streak cur:", loss_streak_cur)

            return {
                "user_id": user,
                "win_streak_current": win_streak_cur,
                "win_streak_max": win_streak_max,
                "loss_streak_current": loss_streak_cur,
                "loss_streak_max": loss_streak_max
            }
    except Exception as e:
        print(f"Error fetching data for user {user}: {e}")
    
    return {
        "user_id": user,
        "win_streak_current": None,
        "win_streak_max": None,
        "loss_streak_current": None,
        "loss_streak_max": None
    }

def fetch_streaks_for_users(df):
    streak_data = []

    for user in df['user_id']:
        streak_info = fetch_streaks_for_user(user)
        streak_data.append(streak_info)
    
    streak_df = pd.DataFrame(streak_data)
    return streak_df

df = pd.read_csv('normalized1.csv')

streaks_df = fetch_streaks_for_users(df)

streaks_df.to_csv('.csv', index=False)