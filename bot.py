from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from commands.commands import register_handlers

bot = Client("jee_solver", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

register_handlers(bot)

if __name__ == "__main__":
    bot.run()
