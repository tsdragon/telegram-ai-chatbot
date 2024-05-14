import asyncio
import importlib
import sys
import logging
import os
from pyrogram import Client, filters, handlers
from datetime import datetime
from lib import format_user_input, setup_logging

debug_mode = False
setup_logging(debug=debug_mode)

class TelegramBot:
    def __init__(self, config_module):
        config = importlib.import_module(f"configs.{config_module}")
        self.log = logging.getLogger(__name__)
        self.debug = False
        self.user_locks = {}
        self.processing_messages = set()
        self.handler = self.initialize_handler(config)
        self.allowed_users = config.allowed_users
        self.log_directory = config.log_directory
        self.ai_name = config.ai_name
        self.bot_token = config.telegram_token
        self.api_id = config.pyrogram_api_id
        self.api_hash = config.pyrogram_api_hash

    def initialize_handler(self, config):
        handler_module = importlib.import_module(f"api.{config.handler_class.lower()}")
        HandlerClass = getattr(handler_module, config.handler_class)
        from inspect import signature
        sig = signature(HandlerClass.__init__)
        handler_kwargs = {k: getattr(config, k) for k in sig.parameters.keys() if hasattr(config, k)}
    
        return HandlerClass(**handler_kwargs)
    
    def run(self):
        app = Client(self.ai_name, api_id=self.api_id, api_hash=self.api_hash, bot_token=self.bot_token)
        allowed_user_ids = list(self.allowed_users.values())
        self.log.info(f"init handler for {self.ai_name}")
        app.add_handler(handlers.MessageHandler(self.reset_user_thread, filters.command("reset") & filters.user(allowed_user_ids)))
        app.add_handler(handlers.MessageHandler(self.handle_messages, filters.text & filters.user(allowed_user_ids)))

        app.run()

    async def handle_messages(self, client, message):
        message_id = str(message.id)
        if message_id in self.processing_messages:
            self.log.warning(f"Skipping reprocessing of message {message_id}")
            return
        self.processing_messages.add(message_id)

        user_id = str(message.from_user.id)
        if user_id not in self.user_locks:
            self.user_locks[user_id] = asyncio.Lock()

        try:
            async with self.user_locks[user_id]:
                user_name = message.from_user.first_name
                self.log.info("Received message from user: %s %s" % (user_name, user_id))
                
                if self.debug:
                    self.log.debug(f"Debug Enabled - User ID: {user_id}, User Name: {user_name}, Message ID: {message.id}")
                    await message.reply_text(f"Bot is currenlty in debug mode, AI responses will not be generated. User ID: {user_id}, User Name: {user_name}")
                    return

                user_input = format_user_input(user_name, message.text)
                self.save_log(user_input, user_name)
                
                try:
                    response = await self.handler.get_ai_response(user_input, {user_id: user_name})
                    self.save_log(response, user_name)
                except Exception as e:
                    error_message = str(e)
                    self.log.error(f"Error getting response: {error_message}")
                    response = "An error occurred."
                    self.save_log(error_message, user_name, error=True)
                
                await message.reply_text(response)
                self.log.info(f"Sent response to user {user_name}")
        finally:
            self.processing_messages.remove(message_id)
    
    async def reset_user_thread(self, client, message):
        user_id = str(message.from_user.id)
        self.log.info("Received reset command from user: %s", user_id)
        await self.handler.reset_thread(user_id)
        await message.reply_text("Your conversation has been reset.")
    
    async def handle_reaction(self, client, message):
        self.log.debug(f"Received reaction from user: {message.from_user.first_name}")
        if message.data not in ["like", "fire"]:
            return
        
        chat_id = message.chat.id
        message_id = message.id
        callback_message = await client.get_messages(chat_id, message_ids=message_id)
        if not callback_message.from_user or not callback_message.from_user.is_self:
            return
        
        user_name = message.from_user.first_name
        user_message = await client.get_messages(chat_id, message_ids=message_id - 1)
        
        bot_message_text = callback_message.text
        user_message_text = user_message.text if user_message else "Previous message not found."

        self.log.info(f"Positive reaction from user {user_name} on message {message_id}")
        self.handler.save_training_data(user_message_text, bot_message_text, user_name)
        
        await message.answer()  # Acknowledge the callback to Telegram

    def save_log(self, text, user_name, error=False):
        log_dir = os.path.join(self.log_directory, user_name)
        os.makedirs(log_dir, exist_ok=True)
        iso_datetime = datetime.now().strftime('%Y%m%d')
        chat_log = os.path.join(log_dir, f"chat_{iso_datetime}.txt")
        error_log = os.path.join(log_dir, f"errors_{iso_datetime}.txt")

        file_path = error_log if error else chat_log
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(text + "\n" + "\n")

def main(config_module_name):
    bot = TelegramBot(config_module_name)
    bot.run()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python telegram_bot.py <config_module>")
        sys.exit(1)

    main(sys.argv[1])