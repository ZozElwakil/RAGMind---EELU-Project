"""
RAGMind Telegram Bot.
Main bot application using pyTelegramBotAPI.
"""
import telebot
from telegram_bot.config import bot_settings
from telegram_bot import handlers
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

logger.info("🤖 Initializing RAGMind Telegram Bot...")

# Initialize bot
try:
    bot = telebot.TeleBot(bot_settings.telegram_bot_token)
    logger.info("✅ Bot initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize bot: {str(e)}")
    raise

def print_bot_link():
    """Print bot link to console."""
    try:
        bot_info = bot.get_me()
        bot_link = f"https://t.me/{bot_info.username}"
        logger.info(f"Bot is running! Share this link: {bot_link}")
    except Exception as e:
        logger.error(f"Error getting bot info: {str(e)}")

def setup_handlers():
    """Register all handlers."""
    # Pass bot instance to handlers
    handlers.set_bot(bot)
    
    # Command handlers
    bot.message_handler(commands=['start'])(handlers.start_command)
    bot.message_handler(commands=['help'])(handlers.help_command)
    
    # Text message handler (for queries)
    bot.message_handler(func=lambda message: True)(handlers.handle_message)

def main():
    """Start the bot."""
    logger.info("Setting up message handlers...")
    setup_handlers()
    logger.info("✅ Handlers registered")
    
    print_bot_link()
    
    logger.info("🚀 Starting RAGMind Telegram Bot...")
    logger.info("Bot will run indefinitely (infinity_polling)")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
