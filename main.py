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

init_db()

# --- ASOSIY MENYU TUGMALARI ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("➕ Bot yaratish"), types.KeyboardButton("📜 Mening botlarim"))
    markup.add(types.KeyboardButton("📊 Statistika"), types.KeyboardButton("❓ Yordam"))
    return markup

# --- HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Assalomu alaykum! Men **Multi-Bot Konstruktorman** 🚀\n\n"
        "Men orqali o'z shaxsiy Kino botingizni yaratishingiz mumkin.\n"
        "Boshlash uchun tugmalardan foydalaning.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.message_handler(lambda message: message.text == "➕ Bot yaratish")
async def start_creation(message: types.Message):
    await message.reply(
        "Ajoyib! Shaxsiy **Kino Bot** yaratish uchun menga @BotFather dan olgan **API Token**ingizni yuboring.\n\n"
        "⚠️ Eslatma: Tokenni yuborishdan oldin botingizga rasm va tavsif o'rnatganingizga ishonch hosil qiling.",
        parse_mode="Markdown"
    )

@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def get_stats(message: types.Message):
    db = SessionLocal()
    count = db.query(CreatedBot).count()
    db.close()
    await message.reply(f"📊 Tizimdagi jami botlar soni: {count} ta")

@dp.message_handler(lambda message: message.text == "📜 Mening botlarim")
async def my_bots(message: types.Message):
    db = SessionLocal()
    user_bots = db.query(CreatedBot).filter(CreatedBot.owner_id == message.from_user.id).all()
    db.close()
    
    if user_bots:
        text = "Sizning botlaringiz:\n\n"
        for b in user_bots:
            text += f"🤖 Token: `{b.token[:15]}...` (Kino bot)\n"
        await message.reply(text, parse_mode="Markdown")
    else:
        await message.reply("Sizda hali botlar yo'q. 'Bot yaratish' tugmasini bosing.")

# Token kelganda ishlovchi qism
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
            
            # Webhook o'rnatish
            user_bot = Bot(token=token)
            await user_bot.set_webhook(f"{RENDER_URL}/webhook/{token}")
            await user_bot.close()
            
            await message.reply(
                f"✅ Tabriklayman! Botingiz ishga tushdi.\n\n"
                f"Endi botingizga o'tib `/start` bosib ko'rishingiz mumkin.",
                reply_markup=main_menu()
            )
        except Exception as e:
            db.rollback()
            await message.reply("❌ Xatolik: Bu token allaqachon foydalanilgan yoki yaroqsiz.")
        finally:
            db.close()
    else:
        await message.reply("⚠️ Bu to'g'ri token emas. Iltimos, @BotFather bergan tokenni yuboring.")

# --- WEBHOOK SOZLAMALARI ---
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
