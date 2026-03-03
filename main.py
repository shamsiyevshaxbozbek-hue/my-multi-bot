import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import configure_app
from aiohttp import web
from database import SessionLocal, CreatedBot, init_db

# 1. SOZLAMALAR
API_TOKEN = '8639736341:AAGaGauSNS4cTC-xNZxHsB0NS0A6BXnaekU'
RENDER_URL = "https://my-multi-bot.onrender.com"
ADMIN_ID = 7031820107

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- ASOSIY MENYU ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Bot yaratish", "📊 Statistika")
    markup.add("📜 Mening botlarim")
    return markup

# --- HANDLERLAR ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Assalomu alaykum! Men Multi-Bot Konstruktorman 🚀\n\n"
        "Kino bot yaratish uchun 'Bot yaratish' tugmasini bosing.",
        reply_markup=main_menu()
    )

@dp.message_handler(lambda m: m.text == "📊 Statistika")
async def get_stats(message: types.Message):
    db = SessionLocal()
    count = db.query(CreatedBot).count()
    db.close()
    await message.reply(f"📊 Jami botlar soni: {count} ta")

@dp.message_handler(lambda m: m.text == "➕ Bot yaratish")
async def ask_token(message: types.Message):
    await message.reply("Kino bot yaratish uchun @BotFather-dan olgan API Tokeningizni yuboring:")

@dp.message_handler()
async def handle_token(message: types.Message):
    token = message.text.strip()
    if ":" in token and len(token) > 20:
        db = SessionLocal()
        try:
            new_bot = CreatedBot(owner_id=message.from_user.id, token=token, bot_type="kino")
            db.add(new_bot)
            db.commit()
            
            # Yangi botni webhookga ulash
            u_bot = Bot(token=token)
            await u_bot.set_webhook(f"{RENDER_URL}/webhook/{token}")
            await u_bot.close()
            
            await message.reply("✅ Tabriklayman! Botingiz yaratildi. Endi o'z botingizga kiring.")
        except:
            db.rollback()
            await message.reply("❌ Xato: Bu token allaqachon foydalanilgan.")
        finally: db.close()

# --- USER BOTLAR UCHUN WEBHOOK --
async def user_bot_webhook(request):
    token = request.match_info.get('token')
    try:
        data = await request.json()
        # Bot ob'ektini yaratamiz
        u_bot = Bot(token=token)
        update = types.Update.to_object(data)
        
        if update.message:
            # Xabarga javob qaytarish
            await u_bot.send_message(update.message.chat.id, "🎬 Kino botingiz xizmatga tayyor!")
        
        # Muhim: Sessiyani yopamiz
        session = await u_bot.get_session()
        await session.close()
        
    except Exception as e:
        logging.error(f"Webhook xatosi: {e}")
    
    return web.Response(text="ok")
# --- SERVERNI ISHGA TUSHIRISH ---
async def on_startup(app):
    init_db() # Ma'lumotlar bazasini ishga tushirish
    await bot.set_webhook(f"{RENDER_URL}/master_webhook")

async def on_shutdown(app):
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()

if __name__ == '__main__':
    app = web.Application()
    
    # User botlar uchun yo'l
    app.router.add_post('/webhook/{token}', user_bot_webhook)
    
    # Master bot uchun webhookni sozlash (bu usul AttributeError'ni oldini oladi)
    configure_app(dp, app, path='/master_webhook')
    
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host='0.0.0.0', port=port)
