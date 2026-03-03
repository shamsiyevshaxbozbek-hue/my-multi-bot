import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from database import SessionLocal, CreatedBot, init_db

# 1. SOZLAMALAR
API_TOKEN = '8639736341:AAGaGauSNS4cTC-xNZxHsB0NS0A6BXnaekU'
# Bu yerda oxirida /webhook bo'lmasin!
RENDER_URL = "https://my-multi-bot.onrender.com" 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Bazani tekshirish/yaratish
init_db()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 Salom! Men Master Botman. Bot tokenini yuboring.")

@dp.message_handler()
async def save_token(message: types.Message):
    token = message.text.strip()
    if ":" in token and len(token) > 20:
        db = SessionLocal()
        try:
            new_bot = CreatedBot(owner_id=message.from_user.id, token=token, bot_type="kino")
            db.add(new_bot)
            db.commit()
            await message.reply("✅ Token Neon bazasiga saqlandi!")
        except Exception as e:
            db.rollback()
            await message.reply("❌ Bu token bazada bor yoki xatolik yuz berdi.")
        finally:
            db.close()
    else:
        await message.reply("⚠️ Bu to'g'ri bot tokeni emas!")

async def on_startup(dp):
    # Webhookni Telegramga bildirish
    await bot.set_webhook(f"{RENDER_URL}/webhook")

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    executor.start_webhook(
        dispatcher=dp,
        webhook_path='/webhook',
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host='0.0.0.0',
        port=port,
    )
