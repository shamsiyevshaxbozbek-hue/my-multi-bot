import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import WebhookRequestHandler
from aiohttp import web
from database import SessionLocal, CreatedBot, init_db

# 1. SOZLAMALAR
API_TOKEN = '8639736341:AAGaGauSNS4cTC-xNZxHsB0NS0A6BXnaekU'
RENDER_URL = "https://my-multi-bot.onrender.com"
ADMIN_ID = 7031820107

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

init_db()

# --- HANDLERLAR ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Bot yaratish", "📊 Statistika")
    await message.reply("Assalomu alaykum! Kino bot yaratish uchun tokenni yuboring.", reply_markup=markup)

@dp.message_handler(lambda m: m.text == "📊 Statistika")
async def get_stats(message: types.Message):
    db = SessionLocal()
    count = db.query(CreatedBot).count()
    db.close()
    await message.reply(f"📊 Jami botlar: {count} ta")

@dp.message_handler()
async def handle_token(message: types.Message):
    token = message.text.strip()
    if ":" in token and len(token) > 20:
        db = SessionLocal()
        try:
            new_bot = CreatedBot(owner_id=message.from_user.id, token=token, bot_type="kino")
            db.add(new_bot)
            db.commit()
            
            # Yangi botni webhookga ulaymiz
            u_bot = Bot(token=token)
            await u_bot.set_webhook(f"{RENDER_URL}/webhook/{token}")
            await u_bot.close()
            await message.reply("✅ Bot yaratildi! Endi o'z botingizga kiring.")
        except:
            db.rollback()
            await message.reply("❌ Xato: Token bazada bor.")
        finally: db.close()

# --- MULTI-BOT DISPATCHER ---
async def user_bot_webhook(request):
    token = request.match_info.get('token')
    # Foydalanuvchi botlari uchun mantiq (shablon)
    u_bot = Bot(token=token)
    data = await request.json()
    update = types.Update.to_object(data)
    
    if update.message:
        await u_bot.send_message(update.message.chat.id, "🎬 Bu kino bot shabloni. Tez orada ishga tushadi!")
    
    await u_bot.close()
    return web.Response(text="ok")

async def on_startup(app):
    await bot.set_webhook(f"{RENDER_URL}/master_webhook")

if __name__ == '__main__':
    app = web.Application()
    # Master bot yo'li
    handler = WebhookRequestHandler(dp)
    app.router.add_post('/master_webhook', handler.handle)
    # User botlar yo'li (404 xatosini yo'qotadi)
    app.router.add_post('/webhook/{token}', user_bot_webhook)
    
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host='0.0.0.0', port=port)
