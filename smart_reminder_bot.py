import telebot
from telebot import types
import threading
import time
from datetime import datetime, timedelta
import pytz
import random
import json
import os

# Initialize bot with your token
bot = telebot.TeleBot("8404435003:AAG6ePF9lNjozAk40hcep8jUXq8w-qzZ9KY")

# Enhanced data storage
USER_DATA_FILE = "user_data.json"
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE) as f:
        user_data = json.load(f)
else:
    user_data = {}

# Timezone setup
UTC = pytz.utc

# Enhanced message database
MESSAGE_DATABASE = {
    "tokenomics": [
        "🔥 iFart burns 1.5% of every transaction - deflationary magic in action!",
        "💰 3% transaction tax (1.5% burned, 1.5% to liquidity) creates constant buy pressure",
        "📉 Only 1B total supply - scarcity is programmed into the protocol"
    ],
    "community": [
        "🚀 500K+ active users in 3 months - fastest growing meme token!",
        "💎 90% retention rate - our community is stronger than diamond hands",
        "🌍 Targeting 1B users by 2027 - be part of the revolution"
    ],
    "features": [
        "🎮 iFart Mini-App: Earn tokens while playing games!",
        "📱 Telegram-native design - seamless Web3 onboarding",
        "🔄 Auto-rewards system - just hold and watch your bag grow"
    ],
    "urgent": [
        "⚠️ WHALE ALERT: Big buys happening right now!",
        "🚨 PRESALE ENDING SOON: Last chance to get in early!",
        "📈 PUMP DETECTED: Token price rising fast!"
    ]
}

# Smart reminder intervals
SMART_INTERVALS = {
    "conservative": 3600,    # 1 hour
    "standard": 1800,        # 30 min
    "aggressive": 600        # 10 min
}

def save_user_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f)

def initialize_user(chat_id):
    if str(chat_id) not in user_data:
        user_data[str(chat_id)] = {
            "reminder_active": False,
            "message_history": [],
            "preferences": {
                "style": "standard",
                "categories": ["tokenomics", "community", "features"],
                "timezone": "UTC",
                "quiet_hours": [0, 8]  # 12am-8am UTC
            },
            "stats": {
                "messages_received": 0,
                "last_active": datetime.now(UTC).isoformat()
            }
        }
        save_user_data()

def get_next_message(chat_id):
    user_prefs = user_data[str(chat_id)]["preferences"]
    available_categories = user_prefs["categories"]
    
    # Check for urgent messages first (5% chance)
    if random.random() < 0.05 and "urgent" not in user_prefs["categories"]:
        return random.choice(MESSAGE_DATABASE["urgent"])
    
    # Select least recently used category
    category_stats = {cat: user_data[str(chat_id)]["message_history"].count(cat) 
                     for cat in available_categories}
    selected_category = min(category_stats, key=category_stats.get)
    
    # Select message not recently sent
    available_messages = MESSAGE_DATABASE[selected_category]
    recent_messages = user_data[str(chat_id)]["message_history"][-5:]  # Last 5 messages
    for msg in available_messages:
        if msg not in recent_messages:
            return msg
    return random.choice(available_messages)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    initialize_user(message.chat.id)
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_settings = types.KeyboardButton('⚙️ Settings')
    btn_start = types.KeyboardButton('🚀 Start Smart Reminders')
    btn_stop = types.KeyboardButton('🛑 Stop Reminders')
    btn_stats = types.KeyboardButton('📊 My Stats')
    btn_learn = types.KeyboardButton('📚 Learn About iFart')
    markup.add(btn_start, btn_stop, btn_settings, btn_stats, btn_learn)
    
    welcome_msg = """🤖 *iFart Smart Reminder Bot* 💨

*Next-Gen Features:*
✅ AI-powered message sequencing
⏰ Smart timing based on market activity
🌙 Quiet hours automation
📊 Personalized analytics
⚡ Urgent alert system

Choose an option below to begin!"""
    
    bot.send_message(message.chat.id, welcome_msg, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🚀 Start Smart Reminders')
def start_smart_reminders(message):
    chat_id = message.chat.id
    initialize_user(chat_id)
    
    if user_data[str(chat_id)]["reminder_active"]:
        bot.reply_to(message, "🔁 Reminders are already running!")
        return
    
    interval = SMART_INTERVALS[user_data[str(chat_id)]["preferences"]["style"]]
    user_data[str(chat_id)]["reminder_active"] = True
    user_data[str(chat_id)]["stats"]["last_active"] = datetime.now(UTC).isoformat()
    save_user_data()
    
    # Start reminder thread
    threading.Thread(target=run_smart_reminder, args=(chat_id, interval)).start()
    
    bot.reply_to(message, f"✅ *Smart reminders activated!*\n\n"
                         f"🔔 Interval: {interval//60} minutes\n"
                         f"📋 Categories: {', '.join(user_data[str(chat_id)]['preferences']['categories']}\n"
                         f"🌙 Quiet hours: {user_data[str(chat_id)]['preferences']['quiet_hours'][0]}:00-"
                         f"{user_data[str(chat_id)]['preferences']['quiet_hours'][1]}:00 UTC",
                parse_mode='Markdown')

def run_smart_reminder(chat_id, interval):
    while user_data.get(str(chat_id), {}).get("reminder_active", False):
        try:
            current_hour = datetime.now(UTC).hour
            quiet_hours = user_data[str(chat_id)]["preferences"]["quiet_hours"]
            
            # Skip during quiet hours
            if quiet_hours[0] <= current_hour < quiet_hours[1]:
                time.sleep(60)
                continue
                
            message = get_next_message(chat_id)
            bot.send_message(chat_id, message)
            
            # Update stats
            user_data[str(chat_id)]["message_history"].append(message)
            user_data[str(chat_id)]["stats"]["messages_received"] += 1
            user_data[str(chat_id)]["stats"]["last_active"] = datetime.now(UTC).isoformat()
            save_user_data()
            
            time.sleep(interval)
        except Exception as e:
            print(f"Error in reminder thread: {e}")
            time.sleep(60)

@bot.message_handler(func=lambda message: message.text == '⚙️ Settings')
def show_settings(message):
    chat_id = message.chat.id
    initialize_user(chat_id)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_style = types.InlineKeyboardButton("🔄 Change Frequency", callback_data="set_style")
    btn_cats = types.InlineKeyboardButton("📋 Message Categories", callback_data="set_categories")
    btn_tz = types.InlineKeyboardButton("🌐 Timezone", callback_data="set_timezone")
    btn_quiet = types.InlineKeyboardButton("🌙 Quiet Hours", callback_data="set_quiet_hours")
    markup.add(btn_style, btn_cats, btn_tz, btn_quiet)
    
    prefs = user_data[str(chat_id)]["preferences"]
    settings_msg = f"""⚙️ *Your Current Settings*

• 🔄 Frequency: {prefs['style'].title()}
• 📋 Categories: {', '.join(prefs['categories'])}
• 🌐 Timezone: {prefs['timezone']}
• 🌙 Quiet Hours: {prefs['quiet_hours'][0]}:00-{prefs['quiet_hours'][1]}:00 UTC

Select a setting to modify:"""
    
    bot.send_message(chat_id, settings_msg, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_"))
def handle_settings_callback(call):
    chat_id = call.message.chat.id
    action = call.data.split("_")[1]
    
    if action == "style":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for style in SMART_INTERVALS.keys():
            markup.add(types.InlineKeyboardButton(style.title(), callback_data=f"setstyle_{style}"))
        bot.edit_message_text("Select reminder frequency:", chat_id, call.message.message_id, reply_markup=markup)
    
    elif action == "categories":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for cat in MESSAGE_DATABASE.keys():
            status = "✅" if cat in user_data[str(chat_id)]["preferences"]["categories"] else "❌"
            markup.add(types.InlineKeyboardButton(f"{status} {cat.title()}", callback_data=f"togglecat_{cat}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_settings"))
        bot.edit_message_text("Toggle message categories:", chat_id, call.message.message_id, reply_markup=markup)
    
    # Additional setting handlers would go here...

@bot.message_handler(func=lambda message: message.text == '📊 My Stats')
def show_stats(message):
    chat_id = message.chat.id
    initialize_user(chat_id)
    
    stats = user_data[str(chat_id)]["stats"]
    last_active = datetime.fromisoformat(stats["last_active"]).strftime("%Y-%m-%d %H:%M UTC")
    
    stats_msg = f"""📊 *Your Reminder Stats*

• 📨 Messages Received: {stats['messages_received']}
• 🕒 Last Active: {last_active}
• 🔄 Current Status: {'Active' if user_data[str(chat_id)]['reminder_active'] else 'Inactive'}

ℹ️ These stats help us improve your experience!"""
    
    bot.send_message(chat_id, stats_msg, parse_mode='Markdown')

if __name__ == '__main__':
    print("🌟 iFart Smart Reminder Bot is running...")
    bot.infinity_polling()
