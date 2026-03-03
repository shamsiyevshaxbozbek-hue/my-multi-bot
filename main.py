import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from database import SessionLocal, CreatedBot

TOKEN = "MASTER_BOT_TOKEN"
BASE_URL = "https://sizning-linkigiz.onrender.com" # Render linki

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Har bir bot uchun alohida Dispatcher-larni saqlash
bot_dispatchers = {}

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer("Xush kelibsiz! Bot yaratish uchun tokenni yuboring.")

# Bu funksiya Telegramdan kelgan har bir xabarni tekshiradi
async def handle_webhook(request):
    token = request.match_info.get('token')
    # Xabar qaysi botga kelganini aniqlaymiz va javob beramiz
    # (Bu yerda murakkab mantiq bo'ladi, hozircha master botni yoqamiz)
    return web.Response(text="OK")

def main():
    app = web.Application()
    # Webhook yo'li
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    handler.register(app, path=f"/webhook/{TOKEN}")
    
    setup_application(app, dp, bot=bot)
    
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
