from aiogram import Bot, Dispatcher, types, F
import asyncio
import aiosqlite

async def start_kino_bot(token):
    bot = Bot(token=token)
    dp = Dispatcher()

    @dp.message(F.text.isdigit()) # Agar faqat raqam yozsa (kino kodi)
    async def get_movie(message: types.Message):
        code = message.text
        async with aiosqlite.connect('main_data.db') as db:
            cursor = await db.execute('SELECT file_id, caption FROM movies WHERE bot_token = ? AND movie_code = ?', (token, code))
            movie = await cursor.fetchone()
            
            if movie:
                await message.answer_video(video=movie[0], caption=movie[1])
            else:
                await message.answer("Kechirasiz, bu kod bilan kino topilmadi.")

    print(f"Bot {token[:10]}... ishga tushdi")
    await dp.start_polling(bot)
