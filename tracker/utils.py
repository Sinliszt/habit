from datetime import date, timedelta
from collections import defaultdict

def calculate_streaks(logs, start_date, target_minutes):
    today = date.today()

    minutes_per_day = defaultdict(int)

    for log in logs:
        minutes_per_day[log.date] += log.minutes_done
    qualifying_dates = {
        day for day, 
        minutes in minutes_per_day.items() if minutes >= target_minutes
    }

    current_streak = 0
    longest_streak = 0
    streak = 0
    on_streak = True

    for i in range((today - start_date).days + 1):
        day = today - timedelta(days=i)
        if day in qualifying_dates:
            streak +=1
            if i == 0:
                current_streak = 1
            elif on_streak:
                current_streak += 1
        else:
            on_streak = False
            longest_streak = max(longest_streak, streak)
            streak = 0
    
    longest_streak = max(longest_streak, streak)
    total_minutes_logged = sum(minutes_per_day.values())
    expected_minutes = ((today - start_date).days + 1) * target_minutes

    if expected_minutes > 0:
        completion_percent = round((total_minutes_logged / expected_minutes) * 100, 1)
    else:
        completion_percent = 0.0

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "completion_percent": completion_percent,
    }
