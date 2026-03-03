import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from database import SessionLocal, CreatedBot, init_db

# 1. SOZLAMALAR
API_TOKEN = '8639736341:AAGaGauSNS4cTC-xNZxHsB0NS0A6BXnaekU'
RENDER_URL = "https://my-multi-bot.onrender.com"
ADMIN_ID = 7031820107

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Bazani tayyorlash
init_db()

@dp.message_handler(commands=['stats'])
async def get_stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        db = SessionLocal()
        count = db.query(CreatedBot).count()
        db.close()
        await message.reply(f"📊 Bazadagi jami botlar soni: {count} ta")
    else:
        await message.reply("❌ Siz admin emassiz!")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 Salom! Men Master Botman. Yangi bot tokenini yuboring.")

@dp.message_handler()
async def handle_token(message: types.Message):
    token = message.text.strip()
    if ":" in token and len(token) > 20:
        db = SessionLocal()
        try:
            new_bot = CreatedBot(owner_id=message.from_user.id, token=token, bot_type="kino")
            db.add(new_bot)
            db.commit()
            
            # Yangi bot webhookini o'rnatish
            user_bot = Bot(token=token)
            await user_bot.set_webhook(f"{RENDER_URL}/webhook/{token}")
            await user_bot.close()
            
            await message.reply("✅ Bot muvaffaqiyatli ro'yxatdan o'tdi!")
        except Exception as e:
            db.rollback()
            await message.reply(f"❌ Xatolik: Token allaqachon bor yoki noto'g'ri.")
        finally:
            db.close()
    else:
        await message.reply("⚠️ Noto'g'ri token!")

# Master bot uchun webhook sozlamalari
async def on_startup(dp):
    await bot.set_webhook(f"{RENDER_URL}/master_webhook")

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    
    start_webhook(
        dispatcher=dp,
        webhook_path='/master_webhook',
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host='0.0.0.0',
        port=port,
    )
# Bu funksiya har bir foydalanuvchi botidan kelgan xabarni qayta ishlaydi
async def handle_user_bot_update(token, update_data):
    try:
        user_bot = Bot(token=token)
        update = types.Update.to_object(update_data)
        
        if update.message:
            # Bu yerda kino bot mantiqi bo'ladi
            await user_bot.send_message(
                update.message.chat.id, 
                f"Salom! Men {token[:10]}... botiman. Tez orada bu yerda kinolar bo'ladi!"
            )
        await user_bot.close()
    except Exception as e:
        logging.error(f"User bot xatosi: {e}")

# Lekin aiogram 2.x da start_webhook buni bitta portda qilishni qiyinlashtiradi.
