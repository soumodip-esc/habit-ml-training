import pandas as pd
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
response = supabase.table("activity_logs").select("*").execute()
df = pd.DataFrame(response.data)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values(['user_id', 'timestamp']).reset_index(drop=True)

# Feature 1: day_of_week
df['day_of_week'] = df['timestamp'].dt.dayofweek

# Feature 2: is_weekend
df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

# Feature 3: frequency_encoded
frequency_map = {'daily': 3, 'weekly': 2, 'rarely': 1}
df['frequency_encoded'] = df['frequency'].map(frequency_map).fillna(0).astype(int)

results = []

for user_id, group in df.groupby('user_id'):
    group = group.copy().reset_index(drop=True)

    # Feature 4: days_since_start
    first_day = group['timestamp'].min()
    group['days_since_start'] = (group['timestamp'] - first_day).dt.days

    # Feature 5: completion_rate_7d
    group['completion_rate_7d'] = (
        group['tasks_completed']
        .rolling(window=7, min_periods=1)
        .mean()
        .round(3)
    )

    # Feature 6: completion_rate_30d
    group['completion_rate_30d'] = (
        group['tasks_completed']
        .rolling(window=30, min_periods=1)
        .mean()
        .round(3)
    )

    # Feature 7: current_streak
    group['current_streak'] = range(1, len(group) + 1)

    results.append(group)

df_features = pd.concat(results, ignore_index=True)

cols = [
    'user_id', 'timestamp', 'day_of_week', 'is_weekend',
    'current_streak', 'completion_rate_7d', 'completion_rate_30d',
    'days_since_start', 'frequency_encoded', 'tasks_completed'
]

df_final = df_features[cols]
df_final.to_csv('ml_dataset.csv', index=False)
print("Dataset saved! Shape:", df_final.shape)
print(df_final.head(10))
