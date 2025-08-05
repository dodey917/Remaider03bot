import threading
import time
from datetime import datetime, timedelta
import pytz
from database import UserDatabase
from config import INTERVAL_PROFILES

class SmartScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.db = UserDatabase()
        self.active_threads = {}
        
    def start_reminders(self, chat_id):
        user = self.db.get_user(chat_id)
        if user["reminder_settings"]["active"]:
            return False
            
        user["reminder_settings"]["active"] = True
        self.db.save_data()
        
        thread = threading.Thread(
            target=self._reminder_loop,
            args=(chat_id,),
            daemon=True
        )
        thread.start()
        self.active_threads[chat_id] = thread
        return True
    
    def _reminder_loop(self, chat_id):
        user = self.db.get_user(chat_id)
        while user["reminder_settings"]["active"]:
            try:
                current_time = datetime.now(pytz.utc)
                
                # Check quiet hours
                if self._in_quiet_hours(user, current_time):
                    time.sleep(60)
                    continue
                
                # Calculate dynamic interval
                interval = self._calculate_interval(user, current_time)
                
                # Send message
                message = self._select_message(user)
                self.bot.send_message(chat_id, message)
                
                # Update tracking
                user["reminder_settings"]["last_sent"] = current_time.isoformat()
                user["reminder_settings"]["message_count"] += 1
                self.db.save_data()
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error in reminder loop: {e}")
                time.sleep(60)
    
    def _calculate_interval(self, user, current_time):
        profile = INTERVAL_PROFILES[user["reminder_settings"]["profile"]]
        base_interval = profile["base_interval"]
        
        # Market hours boost (9AM-5PM UTC)
        if 9 <= current_time.hour < 17:
            base_interval /= profile["market_hours_boost"]
        
        # TODO: Add volatility-based adjustments from API
        return max(base_interval, 300)  # Minimum 5 minutes
    
    def _in_quiet_hours(self, user, current_time):
        start, end = user["preferences"]["quiet_hours"]
        return start <= current_time.hour < end
    
    def _select_message(self, user):
        # TODO: Implement smart message selection
        return "Sample reminder message"
