import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.webhook import WebhookRequestHandler
from database import SessionLocal, CreatedBot, init_db

# 1. SOZLAMALAR
API_TOKEN = '8639736341:AAGaGauSNS4cTC-xNZxHsB0NS0A6BXnaekU'
RENDER_URL = "https://my-multi-bot.onrender.com"
ADMIN_ID = 7031820107  # O'zingizning ID'ngizni yozganingizga ishonch hosil qiling

logging.basicConfig(level=logging.INFO)

# Master Bot
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

init_db()

# --- ADMIN STATISTIKA ---
@dp.message_handler(commands=['stats'])
async def get_stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        db = SessionLocal()
        count = db.query(CreatedBot).count()
        db.close()
        await message.reply(f"📊 Bazadagi jami botlar soni: {count} ta")
    else:
        await message.reply("❌ Siz admin emassiz!")

# --- MASTER BOT START ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 Salom! Men Master Botman. Yangi bot tokenini yuboring.")

# --- TOKEN QABUL QILISH VA ISHGA TUSHIRISH ---
@dp.message_handler()
async def handle_token(message: types.Message):
    token = message.text.strip()
    if ":" in token and len(token) > 20:
        db = SessionLocal()
        try:
            # Bazaga saqlash
            new_bot = CreatedBot(owner_id=message.from_user.id, token=token, bot_type="kino")
            db.add(new_bot)
            db.commit()
            
            # Yangi botni Telegram Webhook-ga ulaymiz
            user_bot = Bot(token=token)
            await user_bot.set_webhook(f"{RENDER_URL}/webhook/{token}")
            await user_bot.close()
            
            await message.reply("✅ Bot muvaffaqiyatli ro'yxatdan o'tdi va ishga tushirildi!")
        except Exception as e:
            db.rollback()
            await message.reply("❌ Xatolik: Token noto'g'ri yoki allaqachon mavjud.")
        finally:
            db.close()
    else:
        await message.reply("⚠️ Noto'g'ri token!")

# --- MULTI-BOT WEBHOOK MANTIQI ---
# Bu qism barcha botlardan keladigan xabarlarni bitta nuqtada tutib oladi
async def handle_user_bots(request):
    token = request.match_info.get('token')
    # Bu yerda kelajakda har bir user bot nima javob berishini yozamiz
    # Hozircha ular shunchaki "Salom" deb javob beradi
    return WebhookRequestHandler(dp)

async def on_startup(app):
    await bot.set_webhook(f"{RENDER_URL}/master_webhook")

if __name__ == '__main__':
    from aiohttp import web
    
    app = web.Application()
    # Master bot uchun yo'l
    executor.setup_webapp(dp, app, path='/master_webhook')
    # Barcha boshqa botlar uchun dinamik yo'l
    # Masalan: /webhook/12345:TOKEN
    app.router.add_post('/webhook/{token}', handle_user_bots)
    
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host='0.0.0.0', port=port)
