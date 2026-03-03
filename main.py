import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from database import SessionLocal, CreatedBot, init_db

# 1. SOZLAMALAR
# Bot tokeningiz va Render manzilingiz
API_TOKEN = '8639736341:AAGaGauSNS4cTC-xNZxHsB0NS0A6BXnaekU'
RENDER_URL = "https://my-multi-bot.onrender.com"

# Loggingni faollashtirish (xatolarni ko'rish uchun)
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher ob'ektlari
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Ma'lumotlar bazasini tayyorlash
init_db()

# --- HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Start buyrug'i uchun javob"""
    await message.reply(
        "👋 Salom! Men Master Botman.\n"
        "Menga yangi bot tokenini yuboring, men uni Neon bazasiga saqlayman."
    )

@dp.message_handler()
async def save_token(message: types.Message):
    """Kelgan tokenni tekshirish va bazaga saqlash"""
    token = message.text.strip()
    
    # Token formatini tekshirish
    if ":" in token and len(token) > 20:
        db = SessionLocal()
        try:
            # Token avval saqlanmaganligini tekshirish
            check_bot = db.query(CreatedBot).filter(CreatedBot.token == token).first()
            if check_bot:
                await message.reply("⚠️ Bu token allaqachon bazada bor!")
            else:
                new_bot = CreatedBot(
                    owner_id=message.from_user.id,
                    token=token,
                    bot_type="kino"
                )
                db.add(new_bot)
                db.commit()
                await message.reply("✅ Token muvaffaqiyatli saqlandi!")
        except Exception as e:
            db.rollback()
            logging.error(f"Baza xatosi: {e}")
            await message.reply("❌ Bazaga yozishda xatolik yuz berdi.")
        finally:
            db.close()
    else:
        await message.reply("⚠️ Bu to'g'ri bot tokeni emas!")

# --- WEBHOOK SOZLAMALARI ---

async def on_startup(dp):
    """Bot yurganda webhookni Telegramga bildirish"""
    await bot.set_webhook(f"{RENDER_URL}/webhook")
    logging.info("Webhook o'rnatildi")

async def on_shutdown(dp):
    """Bot to'xtaganda webhookni o'chirish"""
    await bot.delete_webhook()
    logging.info("Webhook o'chirildi")

if __name__ == '__main__':
    # Render portni dinamik beradi, 10000 - standart port
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
