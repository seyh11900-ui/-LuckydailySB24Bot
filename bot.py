import os
import random
import logging
from datetime import time
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# List of daily tips
DAILY_TIPS = [
    "💡 **Tip #1:** Drink at least 8 glasses of water today!",
    "💡 **Tip #2:** Take a 5-minute break for every 45 minutes of focused work.",
    "💡 **Tip #3:** Plan your top 3 tasks for tomorrow before going to bed.",
    "💡 **Tip #4:** Walk at least 7,000 to 10,000 steps daily.",
    "💡 **Tip #5:** Backup important project files regularly.",
    "💡 **Tip #6:** Practice mindfulness or quiet breathing for 3 minutes.",
    "💡 **Tip #7:** Always secure sensitive API keys in environment variables!"
]

def get_random_tip() -> str:
    return random.choice(DAILY_TIPS)

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    
    # Save chat_id in bot's app data for daily broadcasting
    chats = context.bot_data.setdefault("subscribed_chats", set())
    chats.add(user_id)

    keyboard = [
        [InlineKeyboardButton("💡 Get Daily Tip", callback_data="get_tip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome! You are now subscribed to receive daily tips.\n\n"
        "Click the button below anytime to get a quick tip!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Command: /tip
async def tip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_random_tip(), parse_mode="Markdown")

# Inline Button Callback Handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_tip":
        keyboard = [[InlineKeyboardButton("💡 Get Another Tip", callback_data="get_tip")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(get_random_tip(), reply_markup=reply_markup, parse_mode="Markdown")

# Scheduled Job for Auto Daily Tip
async def send_daily_tip(context: ContextTypes.DEFAULT_TYPE):
    chats = context.bot_data.get("subscribed_chats", set())
    tip = f"☀️ **Your Daily Tip:**\n\n{get_random_tip()}"
    
    for chat_id in list(chats):
        try:
            await context.bot.send_message(chat_id=chat_id, text=tip, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send tip to {chat_id}: {e}")

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is missing!")

    # Build Application
    app = Application.builder().token(token).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tip", tip_command))
    app.add_handler(CallbackQueryHandler(button_click))

    # Schedule Daily Job (e.g., Every day at 09:00 AM UTC)
    job_queue = app.job_queue
    if job_queue:
        target_time = time(hour=9, minute=0, second=0, tzinfo=pytz.UTC)
        job_queue.run_daily(send_daily_tip, time=target_time)

    # Start Bot Polling
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
