import time
import os
import schedule
import psutil
from datetime import datetime, timezone
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY, USER_ID

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BOOT_FLAG = "C:\\lab_agent\\boot_flag.txt"

def get_time_bucket(hour):
    if hour < 12:
        return "morning"
    elif hour < 18:
        return "afternoon"
    else:
        return "evening"

def is_fresh_boot():
    if os.path.exists(BOOT_FLAG):
        os.remove(BOOT_FLAG)  # delete flag after reading
        return True
    return False

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
            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=timezone.utc)
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
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now()
    session_count = get_session_count()

    # Check if fresh boot
    if is_fresh_boot():
        session_minutes = 10  # fresh boot default
        print("Fresh boot detected — session set to 10 mins default")
    else:
        last_log = get_last_log_time()
        if last_log:
            session_minutes = int((now_utc - last_log).total_seconds() / 60)
        else:
            session_minutes = 10
        session_minutes = min(session_minutes, 120)

    data = {
        "user_id": USER_ID,
        "session_minutes": session_minutes,
        "tasks_completed": session_count + 1,
        "day_of_week": now_local.weekday(),
        "time_bucket": get_time_bucket(now_local.hour),
        "frequency": "daily"
    }

    try:
        supabase.table("activity_logs").insert(data).execute()
        print(f"Logged at {now_local} | Session: {session_minutes} mins | Count: {session_count + 1}")
    except Exception as e:
        print("Logging failed:", e)

schedule.every(10).minutes.do(log_activity)

print("Logger started. Logging every 10 minutes...")
log_activity()

while True:
    schedule.run_pending()
    time.sleep(1)