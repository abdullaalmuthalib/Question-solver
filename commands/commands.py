from pyrogram import Client, filters
from datetime import datetime
from PIL import Image
import pytesseract
from google.generativeai import GenerativeModel
from config import GEMINI_API_KEY, DAILY_USER_LIMIT, DAILY_GLOBAL_LIMIT

model = GenerativeModel("gemini-1.5-flash", api_key=GEMINI_API_KEY)
REQUESTS = {}  # Format: { "YYYY-MM-DD": {"global": int, "users": {user_id: count}} }

def extract_text(path):
    try:
        return pytesseract.image_to_string(Image.open(path)).strip()
    except Exception as e:
        return f"OCR Error: {e}"

def check_limits(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in REQUESTS:
        REQUESTS[today] = {"global": 0, "users": {}}
    if REQUESTS[today]["global"] >= DAILY_GLOBAL_LIMIT:
        return "⚠️ Daily global limit (1500) reached. Try again tomorrow."
    if REQUESTS[today]["users"].get(user_id, 0) >= DAILY_USER_LIMIT:
        return "⚠️ You have reached your daily limit of 20 questions."
    REQUESTS[today]["global"] += 1
    REQUESTS[today]["users"][user_id] = REQUESTS[today]["users"].get(user_id, 0) + 1
    return None

async def ask_gemini(prompt):
    try:
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"Gemini Error: {e}"

def register_handlers(bot: Client):
    @bot.on_message(filters.command("start"))
    async def start_handler(client, message):
        await message.reply(
            "👋 Welcome to the JEE/NEET Solver Bot!
"
            "Reply to any question (text or image) with /solve to get the solution.

"
            "🔢 Daily Limit: 20 per user, 1500 global."
        )

    @bot.on_message(filters.command("solve") & filters.reply)
    async def solve_reply(client, message):
        user_id = message.from_user.id
        limit_msg = check_limits(user_id)
        if limit_msg:
            await message.reply(limit_msg)
            return
        reply = message.reply_to_message
        if reply.text:
            query = reply.text
        elif reply.photo:
            path = await reply.download()
            query = extract_text(path)
        else:
            await message.reply("❓ Reply to text or image only.")
            return
        await message.reply("🧠 Solving...")
        ans = await ask_gemini(query)
        await message.reply(f"📊 Answer:

{ans}")
