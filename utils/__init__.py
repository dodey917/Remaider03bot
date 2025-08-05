import pytz
from datetime import datetime

def format_time(dt, timezone='UTC'):
    tz = pytz.timezone(timezone)
    return dt.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')

def calculate_engagement_score(user_data):
    """Calculate user engagement score (0-100)"""
    messages = user_data["analytics"]["total_messages"]
    last_active = datetime.fromisoformat(user_data["analytics"]["last_interaction"])
    days_since_active = (datetime.now(pytz.utc) - last_active).days
    
    score = min(messages, 100)  # Base score
    if days_since_active == 0:
        score += 20
    elif days_since_active <= 7:
        score += 10
    return min(score, 100)
