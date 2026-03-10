import time
import schedule
import psutil
from datetime import datetime
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY, USER_ID

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_time_bucket(hour):
    if hour < 12:
        return "morning"
    elif hour < 18:
        return "afternoon"
    else:
        return "evening"

def get_last_log_time():
    try:
        response = supabase.table("activity_logs") \
            .select("timestamp") \
            .eq("user_id", USER_ID) \
            .order("timestamp", desc=True) \
            .limit(1) \
            .execute()

        if response.data:
            last_time = datetime.fromisoformat(response.data[0]['timestamp'])
            # Strip timezone info to match local time
            if last_time.tzinfo is not None:
                last_time = last_time.replace(tzinfo=None)
            return last_time
        return None
    except:
        return None

def get_session_count():
    try:
        response = supabase.table("activity_logs") \
            .select("id", count="exact") \
            .eq("user_id", USER_ID) \
            .execute()
        return response.count
    except:
        return 0

def log_activity():
    now = datetime.now()  # local time
    session_count = get_session_count()

    last_log = get_last_log_time()
    if last_log:
        session_minutes = int((now - last_log).total_seconds() / 60)
    else:
        session_minutes = 10

    session_minutes = min(session_minutes, 120)

    data = {
        "user_id": USER_ID,
        "session_minutes": session_minutes,
        "tasks_completed": session_count + 1,
        "day_of_week": now.weekday(),
        "time_bucket": get_time_bucket(now.hour),
        "frequency": "daily"
    }

    try:
        supabase.table("activity_logs").insert(data).execute()
        print(f"Logged at {now} | Session: {session_minutes} mins | Count: {session_count + 1}")
    except Exception as e:
        print("Logging failed:", e)

schedule.every(10).minutes.do(log_activity)

print("Logger started. Logging every 10 minutes...")
log_activity()

while True:
    schedule.run_pending()
    time.sleep(1)