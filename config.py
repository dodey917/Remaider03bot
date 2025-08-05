# Bot Configuration
BOT_CONFIG = {
    "token": "8404435003:AAG6ePF9lNjozAk40hcep8jUXq8w-qzZ9KY",
    "admin_ids": [12345678],  # Your Telegram ID for admin features
    "max_retries": 3,
    "default_timezone": "UTC",
    "backup_interval": 3600  # Auto-backup every hour
}

# Message Database Enhancement
MESSAGE_CATEGORIES = {
    "tokenomics": {
        "weight": 0.4,
        "priority": 1,
        "cooldown": 2
    },
    "community": {
        "weight": 0.3,
        "priority": 2,
        "cooldown": 3  
    },
    "features": {
        "weight": 0.2,
        "priority": 3,
        "cooldown": 4
    },
    "urgent": {
        "weight": 0.1,
        "priority": 0,
        "cooldown": 0
    }
}

# Smart Interval Settings
INTERVAL_PROFILES = {
    "conservative": {
        "base_interval": 3600,
        "market_hours_boost": 1.5,
        "volatility_multiplier": 0.8
    },
    "standard": {
        "base_interval": 1800,
        "market_hours_boost": 2.0,
        "volatility_multiplier": 1.2
    },
    "aggressive": {
        "base_interval": 600,
        "market_hours_boost": 3.0,
        "volatility_multiplier": 1.5
    }
}
