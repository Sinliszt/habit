from datetime import date, timedelta

def calculate_streaks(log_dates, start_date):
    today = date.today()
    log_dates = set(log_dates)

    current_streak = 0
    longest_streak = 0
    streak = 0

    for i in range((today - start_date).days + 1):
        day = today - timedelta(days=i)
        if day in log_dates:
            streak +=1
            if i == 0:
                current_streak = streak
        else:
            longest_streak = max(longest_streak, streak)
            streak = 0
    
    longest_streak = max(longest_streak, streak)
    total_days = (today-start_date).days + 1
    completion_percent = round((len(log_dates) / total_days) * 100, 1) if total_days > 0 else 0.0

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "completion_percent": completion_percent,
    }
