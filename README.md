# Lab Activity Data Collection System

A lightweight Python-based system that collects behavioral usage data from lab computers, stores it in a Supabase cloud database, and generates ML-ready datasets for predicting user productivity and task completion patterns.

---

## What This Does

- Runs silently in the background on lab computers
- Logs activity every 10 minutes automatically
- Stores data in a centralized Supabase (PostgreSQL) cloud database
- Tracks real session duration, usage patterns, and task counts per user
- Generates a fully engineered ML-ready CSV dataset with 7 features

---

## Project Structure

```
habit-ml-training/
├── .env                    # Your credentials (NOT on GitHub)
├── .gitattributes          # Git attributes config
├── .gitignore              # Prevents .env from being uploaded
├── config.py               # Loads credentials from .env
├── feature_engineering.py  # Transforms raw data into ML features
├── logger.py               # Main data collection agent
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Database | Supabase (PostgreSQL) |
| Activity Monitor | psutil |
| Scheduler | schedule |
| Cloud Client | supabase-py |
| Data Processing | pandas |
| ML Model | scikit-learn |
| Auto-start | Windows Task Scheduler |

---

## Setup From Scratch

### 1. Clone the Repository

```bash
git clone https://github.com/soumodip-esc/lab-activity-system.git
cd lab-activity-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Your Supabase Database

Go to [supabase.com](https://supabase.com), create a new project, then run this in the SQL Editor:

```sql
create table activity_logs (
    id uuid default gen_random_uuid() primary key,
    user_id text,
    timestamp timestamptz default now(),
    session_minutes int,
    tasks_completed int,
    day_of_week int,
    time_bucket text,
    frequency text
);
```

### 4. Configure Environment Variables

Copy the example env file:

```bash
copy .env.example .env
```

Open `.env` and fill in your values:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
USER_ID=LAB_PC_01
```

- Get `SUPABASE_URL` and `SUPABASE_KEY` from Supabase → Project Settings → API
- Set `USER_ID` to a unique name for each computer (LAB_PC_01, LAB_PC_02, etc.)

### 5. Test the Logger

```bash
python logger.py
```

Expected output:
```
Logger started. Logging every 10 minutes...
Logged at 2026-03-10 10:30:00 | Session: 10 mins | Count: 1
```

Check your Supabase Table Editor — you should see a new row in `activity_logs`.

### 6. Set Up Auto-Start (Windows Task Scheduler)

To run the logger automatically on every startup:

1. Open **Task Scheduler** → Create Basic Task
2. Name it: `Lab Activity Logger`
3. Trigger: **When the computer starts**
4. Action: **Start a program**
5. Program: `python`
6. Arguments: `C:\lab_agent\logger.py`
7. Click Finish

---

## Data Collection

The logger collects the following every 10 minutes:

| Field | Description |
|---|---|
| user_id | Unique ID per computer (from .env) |
| timestamp | Local date and time of log |
| session_minutes | Real minutes since last log (capped at 120) |
| tasks_completed | Auto-incrementing count per user |
| day_of_week | 0 = Monday, 6 = Sunday |
| time_bucket | morning / afternoon / evening |
| frequency | Usage frequency pattern |

### Data NOT Collected
- Keystrokes
- Screen recordings
- Personal files
- Browsing history
- Any personal information

---

## Generating the ML Dataset

Once you have collected enough data (recommended: 7+ days), run:

```bash
python feature_engineering.py
```

This pulls all data from Supabase and generates `ml_dataset.csv` with these features:

| Feature | Description |
|---|---|
| day_of_week | 0 = Monday, 6 = Sunday |
| is_weekend | 1 if Saturday or Sunday, else 0 |
| current_streak | Consecutive active log count per user |
| completion_rate_7d | Rolling 7-log average of tasks completed |
| completion_rate_30d | Rolling 30-log average of tasks completed |
| days_since_start | Days since user's first ever log |
| frequency_encoded | daily=3, weekly=2, rarely=1 |

---

## Training the ML Model

```bash
python train_model.py
```

This reads `ml_dataset.csv`, trains a Random Forest classifier, prints accuracy and feature importance, and saves the model as `model.pkl`.

To use your own ML code instead, just load the CSV:

```python
import pandas as pd

df = pd.read_csv('ml_dataset.csv')

X = df[[
    'day_of_week',
    'is_weekend',
    'current_streak',
    'completion_rate_7d',
    'completion_rate_30d',
    'days_since_start',
    'frequency_encoded'
]]

y = df['tasks_completed']
```

---

## Deploying to Multiple Computers

1. Copy the entire `lab_agent` folder to each computer
2. Open `.env` on each machine and change `USER_ID` to a unique value
3. Run `pip install -r requirements.txt`
4. Set up Task Scheduler following Step 6 above

---

## Exporting Data from Supabase

**Option A — From Dashboard:**
Supabase → Table Editor → activity_logs → Export (CSV button top right)

**Option B — Via Python (ML-ready with all features):**
```bash
python feature_engineering.py
```
Generates `ml_dataset.csv` directly.

---

## Expected Dataset Growth

| Duration | Records per Computer |
|---|---|
| 1 Day | ~50–100 |
| 1 Week | ~500–1,000 |
| 1 Month | ~3,000+ |

---

## Troubleshooting

| Error | Fix |
|---|---|
| `Module not found` | Run `pip install -r requirements.txt` |
| `Logging failed: WinError 10060` | Check internet connection or firewall |
| `getaddrinfo failed` | Check SUPABASE_URL in `.env` for typos |
| No data in Supabase | Verify SUPABASE_KEY is the anon/public key |
| All features are 0 | tasks_completed may all be 0 — let logger run longer |
| Time showing wrong timezone | Make sure `datetime.now()` is used not `datetime.now(timezone.utc)` |

---

## Privacy

This system only collects behavioral metrics — no personal data, keystrokes, screen content, or files are ever accessed or stored. All user identifiers are anonymized computer labels set manually in the `.env` file.

---

## Future Enhancements

- Student login tracking
- Task completion UI for manual labeling
- Real-time dashboard
- Automated feature pipeline
- Prediction API
- Early risk detection system
- Usage analytics visualization

---


