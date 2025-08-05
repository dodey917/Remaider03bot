import telebot
from telebot import types
import threading
import time
import json
import os
from datetime import datetime

# Initialize bot
bot = telebot.TeleBot("8404435003:AAG6ePF9lNjozAk40hcep8jUXq8w-qzZ9KY")

# User data storage
USER_DATA_FILE = "user_data.json"

# Load or initialize user data
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE) as f:
        user_data = json.load(f)
else:
    user_data = {}

# Reminder messages (7 unique messages)
REMINDER_MESSAGES = [
    "🚨 BUY NOW BEFORE PRESALE ENDS! Whales 🐳 are coming, fill your bags now!",
    "⚠️ LAST CHANCE! Presale closing soon - whales accumulating $iFART!",
    "📈 PRICE PUMP INCOMING! Load up before the next surge!",
    "💎 DIAMOND HANDS WIN! Secure your $iFART position now!",
    "🔥 1B TOTAL SUPPLY! Don't miss the deflationary tokenomics!",
    "🎮 EARN WHILE YOU PLAY! iFart Mini-App rewards waiting!",
    "🚀 PHASE 3 LAUNCHING SOON! Get positioned before listings!"
]

def save_user_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f)

def initialize_user(chat_id):
    if str(chat_id) not in user_data:
        user_data[str(chat_id)] = {
            "reminder_active": False,
            "current_message_index": 0,
            "reminder_interval": None,
            "last_reminder_time": None
        }
        save_user_data()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    initialize_user(message.chat.id)
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_10min = types.KeyboardButton('⏰ 10min Reminder')
    btn_30min = types.KeyboardButton('⏰ 30min Reminder')
    btn_1hr = types.KeyboardButton('⏰ 1hr Reminder')
    btn_stop = types.KeyboardButton('🛑 Stop Reminders')
    markup.add(btn_10min, btn_30min, btn_1hr, btn_stop)
    
    welcome_msg = """🚀 *iFart Token Reminder Bot* 💨

Set reminders to never miss crucial buying opportunities:

• 10min - For aggressive traders
• 30min - Balanced approach
• 1hr - Conservative strategy

Current Status: {status}""".format(
        status="✅ ACTIVE" if user_data[str(message.chat.id)]["reminder_active"] else "🛑 INACTIVE"
    )
    
    bot.send_message(message.chat.id, welcome_msg, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['⏰ 10min Reminder', '⏰ 30min Reminder', '⏰ 1hr Reminder'])
def set_reminder(message):
    chat_id = message.chat.id
    initialize_user(chat_id)
    
    # Cancel existing reminder if any
    if user_data[str(chat_id)]["reminder_active"]:
        stop_reminders(message)
    
    # Set interval
    if '10min' in message.text:
        interval = 600
        interval_text = "10 minutes"
    elif '30min' in message.text:
        interval = 1800
        interval_text = "30 minutes"
    else:
        interval = 3600
        interval_text = "1 hour"
    
    # Initialize reminder
    user_data[str(chat_id)].update({
        "reminder_active": True,
        "current_message_index": 0,
        "reminder_interval": interval,
        "last_reminder_time": datetime.now().isoformat()
    })
    save_user_data()
    
    # Start reminder thread
    threading.Thread(target=run_reminder, args=(chat_id,)).start()
    
    bot.reply_to(message, f"✅ {interval_text} reminders activated!\n\n"
                         "You'll receive 7 unique messages in sequence, "
                         "each sent once per reminder cycle.")

def run_reminder(chat_id):
    while user_data.get(str(chat_id), {}).get("reminder_active", False):
        try:
            # Get current message
            msg_index = user_data[str(chat_id)]["current_message_index"]
            message = REMINDER_MESSAGES[msg_index]
            
            # Send message
            bot.send_message(chat_id, message)
            
            # Update index (cycle through 7 messages)
            new_index = (msg_index + 1) % len(REMINDER_MESSAGES)
            user_data[str(chat_id)]["current_message_index"] = new_index
            user_data[str(chat_id)]["last_reminder_time"] = datetime.now().isoformat()
            save_user_data()
            
            # Wait for next interval
            interval = user_data[str(chat_id)]["reminder_interval"]
            time.sleep(interval)
            
        except Exception as e:
            print(f"Error in reminder thread: {e}")
            time.sleep(60)

@bot.message_handler(func=lambda message: message.text == '🛑 Stop Reminders')
def stop_reminders(message):
    chat_id = message.chat.id
    if user_data.get(str(chat_id), {}).get("reminder_active", False):
        user_data[str(chat_id)]["reminder_active"] = False
        save_user_data()
        bot.reply_to(message, "🛑 Reminders stopped successfully!")
    else:
        bot.reply_to(message, "⚠️ No active reminders to stop")

if __name__ == '__main__':
    print("iFart Reminder Bot is running...")
    bot.infinity_polling()
