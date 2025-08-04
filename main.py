import os
import random
from threading import Timer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Configuration
BOT_TOKENS = os.environ.get('BOT_TOKENS', "").split(',') or [
    "8229670972:AAFAxmQMxM0Vkfu5s_Gl73GsY4K3qwZ3p8E",
    "8132609297:AAGEbi5QRXfg_Bzs9a2SnqDyE-PKZPHkP3k",
    "8404435003:AAG6ePF9lNjozAk40hcep8jUXq8w-qzZ9KY"
]

REMINDER_MESSAGES = [
    "⏰ Buy now before presale ends! Whale 🐳 are coming, fill your bag now!",
    "🚨 Don't miss out! Presale ending soon - whales are accumulating!""💰 Last chance to buy before price pumps! Fill your bags!",
    "🐳 Whales are buying! Don't be left behind - buy now!",
    "🔥 Hot opportunity! Presale ending soon - get in before it's too late!",
    "🚀 Rocket fuel loading! Buy now before takeoff!",
    "💎 Diamond hands win! Accumulate before the surge!",
    "📈 Charts looking bullish! Time to fill your bags!",
    "🤑 Don't regret later - buy now before price explodes!",
    "⚡ Lightning deal! Last chance before presale closes!,
    # ... (keep your other messages)
]

class RepeatedTimer:
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def cancel(self):
        if self._timer:
            self._timer.cancel()
        self.is_running = False

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("10 min", callback_data='10'),
         InlineKeyboardButton("30 min", callback_data='30'),
         InlineKeyboardButton("1 hour", callback_data='60')],
        [InlineKeyboardButton("❌ Stop Reminders", callback_data='stop')]
    ]
    update.message.reply_text(
        '⏰ Choose reminder interval:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    chat_id = query.message.chat_id
    data = query.data
    
    if 'reminders' not in context.chat_data:
        context.chat_data['reminders'] = {}
    
    if data == 'stop':
        if 'timer' in context.chat_data['reminders']:
            context.chat_data['reminders']['timer'].cancel()
            del context.chat_data['reminders']['timer']
        query.edit_message_text(text="✅ Reminders stopped!")
        return
    
    interval = int(data) * 60
    if 'timer' in context.chat_data['reminders']:
        context.chat_data['reminders']['timer'].cancel()
    
    context.chat_data['reminders']['timer'] = RepeatedTimer(
        interval, 
        send_reminder, 
        context.bot, 
        chat_id
    )
    query.edit_message_text(text=f"🔔 Reminders started! ({data} min interval)")

def send_reminder(bot, chat_id):
    try:
        message = random.choice(REMINDER_MESSAGES)
        bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Error sending reminder: {e}")

def main():
    for i, token in enumerate(BOT_TOKENS, 1):
        if not token.strip():
            continue
            
        updater = Updater(token)
        dispatcher = updater.dispatcher
        
        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CallbackQueryHandler(button_handler))
        
        print(f"Starting bot {i}...")
        updater.start_polling()
    
    print("All bots are running!")
    while True:
        pass

if __name__ == '__main__':
    main()
