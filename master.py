import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from database import init_db, add_user

# O'zingizning @BotFather dan olgan MASTER TOKENingizni bura qo'ying
TOKEN = "8639736341:AAGaGauSNS4cTC-xNZxHsB0NS0A6BXnaekU"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await add_user(message.from_user.id)
    
    # Oddiy tugmalar
    kb = [
        [types.KeyboardButton(text="Bot yaratish 🤖")],
        [types.KeyboardButton(text="Mening botlarim 📂"), types.KeyboardButton(text="Hisobim 💰")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    await message.answer(f"Salom {message.from_user.full_name}!\nBu bot orqali o'z biznesingiz uchun bot yarata olasiz.", reply_markup=keyboard)

@dp.message(F.text == "Bot yaratish 🤖")
async def create_bot(message: types.Message):
    # Shablonlar ro'yxati
    builder = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎬 Kino Bot", callback_data="template_kino")],
        [types.InlineKeyboardButton(text="📞 Navbatga yozilish (Service)", callback_data="template_service")],
        [types.InlineKeyboardButton(text="🛒 Raqamli do'kon", callback_data="template_shop")]
    ])
    await message.answer("Qaysi shablon asosida bot yaratmoqchisiz?", reply_markup=builder)

async def main():
    await init_db() # Bazani ishga tushirish
    print("Master Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import aiosqlite

# Holatlarni yaratamiz
class BotCreation(StatesGroup):
    waiting_for_token = State()
    choosing_template = State()

# Shablon tanlanganda tokenni so'rash
@dp.callback_query(F.data.startswith("template_"))
async def process_template(callback: types.CallbackQuery, state: FSMContext):
    template_type = callback.data.split("_")[1]
    await state.update_data(chosen_template=template_type)
    
    await callback.message.answer("Endi menga @BotFather dan olgan API Tokeningizni yuboring:")
    await state.set_state(BotCreation.waiting_for_token)
    await callback.answer()

# Tokenni qabul qilish va tekshirish
@dp.message(BotCreation.waiting_for_token)
async def get_token(message: types.Message, state: FSMContext):
    token = message.text.strip()
    
    # Tokenni tekshirib ko'ramiz
    try:
        temp_bot = Bot(token=token)
        bot_info = await temp_bot.get_me()
        await temp_bot.session.close() # Sessiyani yopamiz
        
        data = await state.get_data()
        template = data['chosen_template']
        
        # Bazaga saqlash
        async with aiosqlite.connect('main_data.db') as db:
            await db.execute(
                'INSERT INTO user_bots (owner_id, bot_token, bot_type) VALUES (?, ?, ?)',
                (message.from_user.id, token, template)
            )
            await db.commit()
            
        await message.answer(f"Tabriklayman! @{bot_info.username} muvaffaqiyatli ulandi.\n"
                             f"Shablon: {template}\n\n"
                             f"Botni ishga tushirish uchun to'lovni tasdiqlashingiz kerak.")
        await state.clear()
        
    except Exception as e:
        await message.answer("Xato token yubordingiz! Iltimos, @BotFather dan olingan to'g'ri tokenni yuboring.")
