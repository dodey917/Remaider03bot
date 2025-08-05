import json
import os
from datetime import datetime
import pytz
from config import BOT_CONFIG

class UserDatabase:
    def __init__(self):
        self.file_path = "user_data.json"
        self.backup_path = "backups/"
        self.data = self._load_data()
        
    def _load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path) as f:
                return json.load(f)
        return {}
    
    def save_data(self):
        # Create backup before saving
        self._create_backup()
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def _create_backup(self):
        os.makedirs(self.backup_path, exist_ok=True)
        timestamp = datetime.now(pytz.utc).strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.backup_path}user_data_{timestamp}.json"
        with open(backup_file, 'w') as f:
            json.dump(self.data, f)
    
    def get_user(self, chat_id):
        if str(chat_id) not in self.data:
            self._initialize_user(chat_id)
        return self.data[str(chat_id)]
    
    def _initialize_user(self, chat_id):
        self.data[str(chat_id)] = {
            "reminder_settings": {
                "active": False,
                "profile": "standard",
                "last_sent": None,
                "message_count": 0
            },
            "preferences": {
                "categories": ["tokenomics", "community", "features"],
                "timezone": BOT_CONFIG["default_timezone"],
                "quiet_hours": [0, 8]  # 12am-8am UTC
            },
            "analytics": {
                "total_messages": 0,
                "last_interaction": datetime.now(pytz.utc).isoformat(),
                "preferred_category": None
            }
        }
        self.save_data()
    
    def update_analytics(self, chat_id, category):
        user = self.get_user(chat_id)
        user["analytics"]["total_messages"] += 1
        user["analytics"]["last_interaction"] = datetime.now(pytz.utc).isoformat()
        
        # Update preferred category (simple frequency analysis)
        category_counts = user.get("category_counts", {})
        category_counts[category] = category_counts.get(category, 0) + 1
        user["category_counts"] = category_counts
        user["analytics"]["preferred_category"] = max(category_counts, key=category_counts.get)
        
        self.save_data()
