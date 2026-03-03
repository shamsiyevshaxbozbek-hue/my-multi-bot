import aiosqlite

async def init_db():
    async with aiosqlite.connect('main_data.db') as db:
        # Foydalanuvchilar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        # Foydalanuvchi yaratgan botlar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_bots (
                bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER,
                bot_token TEXT UNIQUE,
                bot_type TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (owner_id) REFERENCES users (user_id)
            )
        ''')
        # Kinolar jadvali (Kino bot shabloni uchun)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_token TEXT,
                movie_code TEXT,
                file_id TEXT,
                caption TEXT
            )
        ''')
        await db.commit()

async def add_user(user_id):
    async with aiosqlite.connect('main_data.db') as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        await db.commit()
