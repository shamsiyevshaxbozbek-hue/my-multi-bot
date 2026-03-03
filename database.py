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
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SHU YERGA NUSXALAB OLGAN URI MANZILINGNI QO'Y
DATABASE_URL = "postgresql://postgres.jfpvrhgtvlcixosjrijo:Shaxbozbek5525@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class BotUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)

class CreatedBot(Base):
    __tablename__ = "user_bots"
    id = Column(Integer, primary_key=True)
    owner_id = Column(BigInteger)
    token = Column(String, unique=True)
    bot_type = Column(String)

# Jadvallarni Supabase'da yaratish
Base.metadata.create_all(bind=engine)
