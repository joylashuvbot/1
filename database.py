import asyncpg
import json
from datetime import datetime, date, timedelta
from config import DATABASE_URL, BOT_INSTANCE_ID




# ========== ZODIAC UTILITIES (database.py uchun) ==========

ZODIAC_KEY_TO_NAMES = {
    "qoy": ["Qo'y", "Qo'y (Aries)", "Aries", "♈", "qoy", "qo'y", "qo`y"],
    "buzoq": ["Buqa", "Buzoq", "Buqa (Taurus)", "Taurus", "♉", "buzoq", "buqa"],
    "egizak": ["Egizak", "Egizaklar", "Egizaklar (Gemini)", "Gemini", "♊", "egizak", "egizaklar"],
    "qisqichbaqa": ["Qisqichbaqa", "Qisqichbaqa (Cancer)", "Cancer", "♋", "qisqichbaqa"],
    "arslon": ["Arslon", "Sher", "Sher (Leo)", "Leo", "♌", "arslon", "sher"],
    "sunbula": ["Sunbula", "Qiz", "Qiz (Virgo)", "Virgo", "♍", "sunbula", "qiz"],
    "tarozi": ["Tarozi", "Tarozi (Libra)", "Libra", "♎", "tarozi"],
    "chayon": ["Chayon", "Chayonlar", "Chayonlar (Scorpio)", "Scorpio", "♏", "chayon", "chayonlar"],
    "oqotar": ["O'qotar", "Yoy", "Yoy (Sagittarius)", "Sagittarius", "♐", "oqotar", "yoy"],
    "tog_echkisi": ["Tog' echkisi", "Tog' echkisi (Capricorn)", "Capricorn", "♑", "tog echkisi", "tog' echkisi", "togʻ echkisi"],
    "qovga": ["Qovg'a", "Qovunchi", "Qovunchi (Aquarius)", "Aquarius", "♒", "qovga", "qovg'a", "qovgʻa", "qovunchi"],
    "baliq": ["Baliq", "Baliq (Pisces)", "Pisces", "♓", "baliq"],
}

ZODIAC_NAME_TO_KEY = {}
for key, names in ZODIAC_KEY_TO_NAMES.items():
    for name in names:
        ZODIAC_NAME_TO_KEY[name.lower().replace('’', "'").replace('`', "'").replace('ʻ', "'")] = key


def normalize_zodiac_name(value):
    """Burj nomini canonical kalitga aylantirish uchun yordamchi."""
    if not value:
        return None

    text = str(value)
    text = text.replace('’', "'").replace('`', "'").replace('ʻ', "'")
    text = text.replace('♈', '').replace('♉', '').replace('♊', '')
    text = text.replace('♋', '').replace('♌', '').replace('♍', '')
    text = text.replace('♎', '').replace('♏', '').replace('♐', '')
    text = text.replace('♑', '').replace('♒', '').replace('♓', '')
    text = text.replace('(', ' ').replace(')', ' ')
    text = text.lower().strip()
    text = ' '.join(text.split())

    return ZODIAC_NAME_TO_KEY.get(text) or ZODIAC_NAME_TO_KEY.get(text.replace("'", ''))

async def get_db():
    """Har bir bot instance o'zining alohida database'iga ulanadi"""
    return await asyncpg.connect(DATABASE_URL)


async def init_db():
    """Database jadvallarini yaratish - har bir bot alohida"""
    conn = await get_db()
    try:
        # Asosiy users jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                gender TEXT,
                age INTEGER,
                city TEXT,
                interests TEXT[],
                zodiac TEXT,
                goals TEXT[],
                photo_file_id TEXT,
                photo_base64 TEXT,
                invited_friends INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                bot_instance TEXT DEFAULT 'default'
            )
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS photo_base64 TEXT
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS about TEXT
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS super_likes_used INTEGER DEFAULT 0
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS group_subscribed BOOLEAN DEFAULT FALSE
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS friends_invited INTEGER DEFAULT 0
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_streak INTEGER DEFAULT 0
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_date DATE
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS relationship_mode TEXT DEFAULT 'romantic'
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS ice_breaker TEXT
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS boost_until TIMESTAMP
        """)

        await conn.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS premium_until TIMESTAMP
        """)

        # Likes
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id BIGSERIAL PRIMARY KEY,
                from_user BIGINT NOT NULL,
                to_user BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                bot_instance TEXT DEFAULT 'default',
                UNIQUE(from_user, to_user)
            )
        """)

        await conn.execute("""
            ALTER TABLE likes ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

        # Matches
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id BIGSERIAL PRIMARY KEY,
                user1 BIGINT NOT NULL,
                user2 BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                bot_instance TEXT DEFAULT 'default',
                UNIQUE(user1, user2)
            )
        """)

        await conn.execute("""
            ALTER TABLE matches ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

        # Blocks
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                id BIGSERIAL PRIMARY KEY,
                blocker BIGINT NOT NULL,
                blocked BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                bot_instance TEXT DEFAULT 'default',
                UNIQUE(blocker, blocked)
            )
        """)

        await conn.execute("""
            ALTER TABLE blocks ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

        # Chat messages
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id BIGSERIAL PRIMARY KEY,
                match_id BIGINT NOT NULL,
                sender_id BIGINT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW(),
                bot_instance TEXT DEFAULT 'default'
            )
        """)

        await conn.execute("""
            ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

        # Kunlik limitlar
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_limits (
                id BIGSERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                likes_used INTEGER DEFAULT 0,
                messages_used INTEGER DEFAULT 0,
                super_likes_used INTEGER DEFAULT 0,
                limit_date DATE DEFAULT CURRENT_DATE,
                bot_instance TEXT DEFAULT 'default'
            )
        """)

        await conn.execute("""
            ALTER TABLE daily_limits ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

        # Referral rewards
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS referral_rewards (
                id BIGSERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                referral_count INTEGER DEFAULT 0,
                unlimited_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                bot_instance TEXT DEFAULT 'default'
            )
        """)

        await conn.execute("""
            ALTER TABLE referral_rewards ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

        # Referrals
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id BIGSERIAL PRIMARY KEY,
                referrer_id BIGINT NOT NULL,
                referred_id BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                bot_instance TEXT DEFAULT 'default',
                UNIQUE(referred_id)
            )
        """)

        await conn.execute("""
            ALTER TABLE referrals ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

        # Group members
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS group_members (
                id BIGSERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                invited_by BIGINT,
                joined_at TIMESTAMP DEFAULT NOW(),
                bot_instance TEXT DEFAULT 'default'
            )
        """)

        await conn.execute("""
            ALTER TABLE group_members ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

        # Group invites
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS group_invites (
                id BIGSERIAL PRIMARY KEY,
                inviter_id BIGINT NOT NULL,
                invited_id BIGINT NOT NULL,
                invited_at TIMESTAMP DEFAULT NOW(),
                bot_instance TEXT DEFAULT 'default',
                UNIQUE(inviter_id, invited_id)
            )
        """)

        await conn.execute("""
            ALTER TABLE group_invites ADD COLUMN IF NOT EXISTS bot_instance TEXT DEFAULT 'default'
        """)

    finally:
        await conn.close()


# ========== BOT INSTANCE FILTER ==========
# Har bir query'da bot_instance = BOT_INSTANCE_ID sharti qo'shiladi
# Bu hatto bitta database'da ham alohidalikni ta'minlaydi (tavsiya etilmaydi)
# ENG YAXSHI YECHIM: Har bir bot uchun alohida database!


# ========== DAILY LIMITS ==========

async def get_daily_limits(telegram_id):
    """Bugungi kunlik limitlarni olish."""
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            """SELECT likes_used, messages_used, super_likes_used, limit_date 
               FROM daily_limits 
               WHERE telegram_id = $1 AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )

        today = date.today()

        if row:
            if row['limit_date'] < today:
                await conn.execute(
                    """UPDATE daily_limits
                       SET likes_used = 0, messages_used = 0, super_likes_used = 0, limit_date = $1
                       WHERE telegram_id = $2 AND bot_instance = $3""",
                    today, telegram_id, BOT_INSTANCE_ID
                )
                return {'likes_used': 0, 'messages_used': 0, 'super_likes_used': 0}
            return {
                'likes_used': row['likes_used'],
                'messages_used': row['messages_used'],
                'super_likes_used': row['super_likes_used']
            }
        else:
            await conn.execute(
                """INSERT INTO daily_limits (telegram_id, likes_used, messages_used, super_likes_used, limit_date, bot_instance) 
                   VALUES ($1, 0, 0, 0, $2, $3)""",
                telegram_id, today, BOT_INSTANCE_ID
            )
            return {'likes_used': 0, 'messages_used': 0, 'super_likes_used': 0}
    finally:
        await conn.close()


async def is_unlimited(telegram_id):
    """Foydalanuvchi limitsiz davrda ekanligini tekshirish"""
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            """SELECT unlimited_until FROM referral_rewards 
               WHERE telegram_id = $1 AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )
        if row and row['unlimited_until']:
            return row['unlimited_until'] > datetime.now()
        return False
    finally:
        await conn.close()


async def check_and_increment_limit(telegram_id, limit_type):
    """Limitni tekshirish va oshirish"""
    unlimited = await is_unlimited(telegram_id)
    if unlimited:
        return True

    limits = await get_daily_limits(telegram_id)

    MAX_LIKES = 25
    MAX_MESSAGES = 10
    MAX_SUPER_LIKES = 10

    if limit_type == 'likes':
        if limits['likes_used'] >= MAX_LIKES:
            return False
        await _increment_limit(telegram_id, 'likes_used')
        return True
    elif limit_type == 'messages':
        if limits['messages_used'] >= MAX_MESSAGES:
            return False
        await _increment_limit(telegram_id, 'messages_used')
        return True
    elif limit_type == 'super_likes':
        if limits['super_likes_used'] >= MAX_SUPER_LIKES:
            return False
        await _increment_limit(telegram_id, 'super_likes_used')
        return True
    return False


async def _increment_limit(telegram_id, column):
    """Limit maydonini 1 ga oshirish"""
    conn = await get_db()
    try:
        await conn.execute(
            f"""UPDATE daily_limits
                SET {column} = {column} + 1
                WHERE telegram_id = $1 AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )
    finally:
        await conn.close()


async def get_limit_status(telegram_id):
    """Foydalanuvchining to'liq limit statusini olish"""
    unlimited = await is_unlimited(telegram_id)
    if unlimited:
        return {
            'unlimited': True,
            'likes_remaining': 999,
            'messages_remaining': 999,
            'super_likes_remaining': 999
        }

    limits = await get_daily_limits(telegram_id)
    MAX_LIKES = 25
    MAX_MESSAGES = 10
    MAX_SUPER_LIKES = 10

    return {
        'unlimited': False,
        'likes_used': limits['likes_used'],
        'likes_remaining': max(0, MAX_LIKES - limits['likes_used']),
        'messages_used': limits['messages_used'],
        'messages_remaining': max(0, MAX_MESSAGES - limits['messages_used']),
        'super_likes_used': limits['super_likes_used'],
        'super_likes_remaining': max(0, MAX_SUPER_LIKES - limits['super_likes_used'])
    }


# ========== REFERRAL REWARDS ==========

async def process_referral(referrer_id, referred_id):
    """Yangi referral qayta ishlash"""
    conn = await get_db()
    try:
        existing = await conn.fetchrow(
            """SELECT id FROM referrals 
               WHERE referred_id = $1 AND bot_instance = $2""",
            referred_id, BOT_INSTANCE_ID
        )
        if existing:
            return False, "Bu foydalanuvchi avval referral qilgan."

        if referrer_id == referred_id:
            return False, "O'zingizni qo'sha olmaysiz."

        await conn.execute(
            """INSERT INTO referrals (referrer_id, referred_id, bot_instance) 
               VALUES ($1, $2, $3) ON CONFLICT DO NOTHING""",
            referrer_id, referred_id, BOT_INSTANCE_ID
        )

        await conn.execute("""
            INSERT INTO referral_rewards (telegram_id, referral_count, updated_at, bot_instance)
            VALUES ($1, 1, NOW(), $2)
            ON CONFLICT (telegram_id) DO UPDATE SET
                referral_count = referral_rewards.referral_count + 1,
                updated_at = NOW()
            WHERE referral_rewards.bot_instance = $2
        """, referrer_id, BOT_INSTANCE_ID)

        row = await conn.fetchrow(
            """SELECT referral_count FROM referral_rewards 
               WHERE telegram_id = $1 AND bot_instance = $2""",
            referrer_id, BOT_INSTANCE_ID
        )
        count = row['referral_count'] if row else 0

        if count == 5:
            until = datetime.now() + timedelta(days=7)
            await conn.execute(
                """UPDATE referral_rewards SET unlimited_until = $1 
                   WHERE telegram_id = $2 AND bot_instance = $3""",
                until, referrer_id, BOT_INSTANCE_ID
            )
            return True, f"🎉 Tabriklaymiz! {count} ta odam qo'shdingiz. 1 hafta limitsiz foydalanish!"
        elif count == 10:
            until = datetime.now() + timedelta(days=30)
            await conn.execute(
                """UPDATE referral_rewards SET unlimited_until = $1 
                   WHERE telegram_id = $2 AND bot_instance = $3""",
                until, referrer_id, BOT_INSTANCE_ID
            )
            return True, f"🎉 Ajoyib! {count} ta odam qo'shdingiz. 1 oy limitsiz foydalanish!"

        return True, f"✅ {count} ta odam qo'shildi. 5 tagacha: 1 hafta, 10 tagacha: 1 oy limitsiz."
    finally:
        await conn.close()


async def get_referral_status(telegram_id):
    """Referral statusini olish"""
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            """SELECT referral_count, unlimited_until FROM referral_rewards 
               WHERE telegram_id = $1 AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )
        if row:
            return {
                'referral_count': row['referral_count'],
                'unlimited_until': row['unlimited_until'].isoformat() if row['unlimited_until'] else None,
                'is_unlimited': row['unlimited_until'] > datetime.now() if row['unlimited_until'] else False
            }
        return {'referral_count': 0, 'unlimited_until': None, 'is_unlimited': False}
    finally:
        await conn.close()


async def get_referral_link(telegram_id, bot_username):
    """Referral link yaratish"""
    return f"https://t.me/{bot_username}?start=ref_{telegram_id}"


async def touch_user_activity(telegram_id):
    """Daily streak va faoliyat tarixini yangilash"""
    conn = await get_db()
    try:
        today = date.today()
        row = await conn.fetchrow(
            """SELECT daily_streak, last_active_date FROM users 
               WHERE telegram_id = $1 AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )

        if row:
            streak = int(row['daily_streak'] or 0)
            last_active = row['last_active_date']

            if last_active is None:
                streak = 1
            elif last_active < today:
                streak = streak + 1 if last_active == today - timedelta(days=1) else 1

            await conn.execute(
                """UPDATE users SET daily_streak = $1, last_active_date = $2 
                   WHERE telegram_id = $3 AND bot_instance = $4""",
                streak, today, telegram_id, BOT_INSTANCE_ID
            )
            return {'daily_streak': streak, 'last_active_date': today.isoformat()}

        await conn.execute(
                    """INSERT INTO users (telegram_id, daily_streak, last_active_date, bot_instance) 
                    VALUES ($1, 1, $2, $3) ON CONFLICT (telegram_id) DO UPDATE 
                    SET daily_streak = users.daily_streak + 1, last_active_date = EXCLUDED.last_active_date""",
                    telegram_id, today, BOT_INSTANCE_ID
                )
        return {'daily_streak': 1, 'last_active_date': today.isoformat()}
    finally:
        await conn.close()


async def get_user_activity_stats(telegram_id):
    """Foydalanuvchi faoliyat statistikasi"""
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            """SELECT daily_streak, last_active_date, relationship_mode, ice_breaker 
               FROM users WHERE telegram_id = $1 AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )
        if row:
            return {
                'daily_streak': int(row['daily_streak'] or 0),
                'last_active_date': row['last_active_date'].isoformat() if row['last_active_date'] else None,
                'relationship_mode': row['relationship_mode'] or 'romantic',
                'ice_breaker': row['ice_breaker'] or 'Qaysi film yoki musiqa sizni eng ko\'proq qiziqtiradi?',
            }
        return {'daily_streak': 0, 'last_active_date': None, 'relationship_mode': 'romantic', 'ice_breaker': 'Qaysi film yoki musiqa sizni eng ko\'proq qiziqtiradi?'}
    finally:
        await conn.close()


async def get_daily_recommendations(telegram_id, limit=5):
    """Bugun uchun tavsiya qilingan profillar"""
    conn = await get_db()
    try:
        rows = await conn.fetch(
            """SELECT telegram_id, username, full_name, gender, age, city, about, interests, zodiac, goals, photo_file_id, photo_base64
               FROM users
               WHERE telegram_id != $1 AND is_active = TRUE AND bot_instance = $3
               ORDER BY random()
               LIMIT $2""",
            telegram_id, limit, BOT_INSTANCE_ID
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


# ========== USER FUNCTIONS ==========

async def save_user(telegram_id, data):
    conn = await get_db()
    try:
        await conn.execute("""
            INSERT INTO users (
                telegram_id, username, full_name, gender, age, city, about, interests,
                zodiac, goals, photo_file_id, photo_base64, relationship_mode, ice_breaker, bot_instance
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            ON CONFLICT (telegram_id) DO UPDATE SET
                username = EXCLUDED.username,
                full_name = EXCLUDED.full_name,
                gender = EXCLUDED.gender,
                age = EXCLUDED.age,
                city = EXCLUDED.city,
                about = EXCLUDED.about,
                interests = EXCLUDED.interests,
                zodiac = EXCLUDED.zodiac,
                goals = EXCLUDED.goals,
                photo_file_id = EXCLUDED.photo_file_id,
                photo_base64 = EXCLUDED.photo_base64,
                relationship_mode = COALESCE(EXCLUDED.relationship_mode, users.relationship_mode),
                ice_breaker = COALESCE(EXCLUDED.ice_breaker, users.ice_breaker),
                is_active = TRUE,
                bot_instance = $15
        """,
            telegram_id,
            data.get("username"),
            data.get("full_name"),
            data.get("gender"),
            data.get("age"),
            data.get("city"),
            data.get("about"),
            data.get("interests", []),
            data.get("zodiac"),
            data.get("goals", []),
            data.get("photo_file_id"),
            data.get("photo_base64"),
            data.get("relationship_mode") or "romantic",
            data.get("ice_breaker"),
            BOT_INSTANCE_ID
        )
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False
    finally:
        await conn.close()

async def get_user(telegram_id):
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            """SELECT * FROM users WHERE telegram_id = $1 AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )
        if row:
            return dict(row)
        return None
    finally:
        await conn.close()


async def search_users(telegram_id, filters):
    conn = await get_db()
    try:
        blocked_ids = await conn.fetch(
            """SELECT blocked FROM blocks WHERE blocker = $1 AND bot_instance = $3
               UNION 
               SELECT blocker FROM blocks WHERE blocked = $1 AND bot_instance = $3""",
            telegram_id, BOT_INSTANCE_ID, BOT_INSTANCE_ID
        )
        excluded = [r["blocked"] for r in blocked_ids] + [telegram_id]

        query = """
            SELECT telegram_id, username, full_name, gender, age, city, about, interests, zodiac, goals, photo_file_id, photo_base64
            FROM users
            WHERE telegram_id != ALL($1::bigint[])
            AND is_active = TRUE
            AND bot_instance = $2
        """
        params = [excluded, BOT_INSTANCE_ID]
        idx = 3

        if filters.get("gender"):
            query += f" AND gender = ${idx}"
            params.append(filters["gender"])
            idx += 1

        if filters.get("age_from"):
            query += f" AND age >= ${idx}"
            params.append(int(filters["age_from"]))
            idx += 1

        if filters.get("age_to"):
            query += f" AND age <= ${idx}"
            params.append(int(filters["age_to"]))
            idx += 1

        if filters.get("city"):
            query += f" AND city ILIKE ${idx}"
            params.append(f"%{filters['city']}%")
            idx += 1

        if filters.get("goals"):
            query += f" AND goals && ${idx}::text[]"
            params.append(filters["goals"])
            idx += 1

        if filters.get("interests"):
            query += f" AND interests && ${idx}::text[]"
            params.append(filters["interests"])
            idx += 1

        if filters.get("name"):
            query += f" AND full_name ILIKE ${idx}"
            params.append(f"%{filters['name']}%")
            idx += 1

        if filters.get("zodiac"):
            query += f" AND zodiac ILIKE ${idx}"
            params.append(f"%{filters['zodiac']}%")
            idx += 1

        query += " LIMIT 50"
        rows = await conn.fetch(query, *params)

        match_rows = await conn.fetch(
            """SELECT user1, user2 FROM matches 
               WHERE (user1 = $1 OR user2 = $1) AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )
        match_ids = set()
        for mr in match_rows:
            other = mr['user1'] if mr['user2'] == telegram_id else mr['user2']
            match_ids.add(other)

        result = []
        for row in rows:
            user = dict(row)
            user['can_write'] = user['telegram_id'] in match_ids
            result.append(user)
        return result
    finally:
        await conn.close()


async def search_users_by_zodiac(telegram_id, filters):
    """Burj mosligiga qarab foydalanuvchilarni qidirish"""
    conn = await get_db()
    try:
        blocked_ids = await conn.fetch(
            """SELECT blocked FROM blocks WHERE blocker = $1 AND bot_instance = $3
               UNION 
               SELECT blocker FROM blocks WHERE blocked = $1 AND bot_instance = $3""",
            telegram_id, BOT_INSTANCE_ID, BOT_INSTANCE_ID
        )
        excluded = [r["blocked"] for r in blocked_ids] + [telegram_id]

        zodiac_keys = filters.get("zodiac_keys", [])
        zodiac_names = filters.get("zodiac_names", [])

        all_names = set()

        if zodiac_keys:
            for key in zodiac_keys:
                names = ZODIAC_KEY_TO_NAMES.get(key, [])
                all_names.update(names)

        for name in zodiac_names:
            key = normalize_zodiac_name(name)
            if key:
                all_names.update(ZODIAC_KEY_TO_NAMES.get(key, []))
            else:
                all_names.add(name)

        if not all_names:
            for key in zodiac_keys:
                all_names.update(ZODIAC_KEY_TO_NAMES.get(key, []))

        zodiac_names = list(all_names)

        if not zodiac_names:
            return []

        query = """
            SELECT telegram_id, username, full_name, gender, age, city, about, interests, zodiac, goals, photo_file_id, photo_base64
            FROM users
            WHERE telegram_id != ALL($1::bigint[])
            AND is_active = TRUE
            AND zodiac IS NOT NULL
            AND bot_instance = $2
        """
        params = [excluded, BOT_INSTANCE_ID]
        idx = 3

        like_conditions = []
        for name in zodiac_names:
            like_conditions.append(f"zodiac ILIKE ${idx}")
            params.append(f"%{name}%")
            idx += 1

        if like_conditions:
            query += " AND (" + " OR ".join(like_conditions) + ")"

        if filters.get("gender"):
            query += f" AND gender = ${idx}"
            params.append(filters["gender"])
            idx += 1

        query += " LIMIT 50"
        rows = await conn.fetch(query, *params)

        match_rows = await conn.fetch(
            """SELECT user1, user2 FROM matches 
               WHERE (user1 = $1 OR user2 = $1) AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )
        match_ids = set()
        for mr in match_rows:
            other = mr['user1'] if mr['user2'] == telegram_id else mr['user2']
            match_ids.add(other)

        result = []
        for row in rows:
            user = dict(row)
            user['can_write'] = user['telegram_id'] in match_ids
            result.append(user)
        return result
    finally:
        await conn.close()


async def add_like(from_user, to_user):
    conn = await get_db()
    try:
        await conn.execute(
            """INSERT INTO likes (from_user, to_user, bot_instance) 
               VALUES ($1, $2, $3) ON CONFLICT DO NOTHING""",
            from_user, to_user, BOT_INSTANCE_ID
        )
        mutual = await conn.fetchrow(
            """SELECT id FROM likes 
               WHERE from_user = $1 AND to_user = $2 AND bot_instance = $3""",
            to_user, from_user, BOT_INSTANCE_ID
        )
        if mutual:
            u1, u2 = min(from_user, to_user), max(from_user, to_user)
            await conn.execute(
                """INSERT INTO matches (user1, user2, bot_instance) 
                   VALUES ($1, $2, $3) ON CONFLICT DO NOTHING""",
                u1, u2, BOT_INSTANCE_ID
            )
            return True
        return False
    finally:
        await conn.close()


async def get_match_id(user1, user2):
    conn = await get_db()
    try:
        u1, u2 = min(user1, user2), max(user1, user2)
        row = await conn.fetchrow(
            """SELECT id FROM matches 
               WHERE user1 = $1 AND user2 = $2 AND bot_instance = $3""",
            u1, u2, BOT_INSTANCE_ID
        )
        return row['id'] if row else None
    finally:
        await conn.close()


async def block_user(blocker, blocked):
    conn = await get_db()
    try:
        await conn.execute(
            """INSERT INTO blocks (blocker, blocked, bot_instance) 
               VALUES ($1, $2, $3) ON CONFLICT DO NOTHING""",
            blocker, blocked, BOT_INSTANCE_ID
        )
    finally:
        await conn.close()


async def get_all_users():
    conn = await get_db()
    try:
        rows = await conn.fetch(
            """SELECT telegram_id, username, full_name, gender, age, city, about, interests, zodiac, goals, photo_file_id, photo_base64, invited_friends, created_at
               FROM users 
               WHERE is_active = TRUE AND bot_instance = $1 
               ORDER BY created_at DESC""",
            BOT_INSTANCE_ID
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_user_stats():
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            """SELECT COUNT(*) AS total, 
                      COUNT(*) FILTER (WHERE gender = 'erkak') AS male, 
                      COUNT(*) FILTER (WHERE gender = 'ayol') AS female, 
                      AVG(age) AS avg_age 
               FROM users 
               WHERE is_active = TRUE AND bot_instance = $1""",
            BOT_INSTANCE_ID
        )
        return dict(row) if row else {'total': 0, 'male': 0, 'female': 0, 'avg_age': None}
    finally:
        await conn.close()


async def get_top_cities(limit=10):
    conn = await get_db()
    try:
        rows = await conn.fetch(
            """SELECT city, COUNT(*) AS count FROM users 
               WHERE city IS NOT NULL AND city <> '' AND is_active = TRUE AND bot_instance = $2
               GROUP BY city ORDER BY count DESC LIMIT $1""",
            limit, BOT_INSTANCE_ID
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def can_write(from_user, to_user):
    """Allow messaging only if match exists"""
    conn = await get_db()
    try:
        match = await conn.fetchrow(
            """SELECT id FROM matches 
               WHERE ((user1 = $1 AND user2 = $2) OR (user1 = $2 AND user2 = $1)) 
               AND bot_instance = $3""",
            from_user, to_user, BOT_INSTANCE_ID
        )
        return match is not None
    finally:
        await conn.close()


async def increment_super_like_usage(from_user):
    conn = await get_db()
    try:
        await conn.execute(
            """UPDATE users SET super_likes_used = COALESCE(super_likes_used, 0) + 1 
               WHERE telegram_id = $1 AND bot_instance = $2""",
            from_user, BOT_INSTANCE_ID
        )
    finally:
        await conn.close()


# ========== CHAT & MATCH FUNCTIONS ==========

async def get_pending_likes(telegram_id):
    conn = await get_db()
    try:
        rows = await conn.fetch("""
            SELECT u.telegram_id, u.username, u.full_name, u.gender, u.age, u.city,
                   u.interests, u.zodiac, u.goals, u.photo_file_id, u.photo_base64, l.created_at
            FROM likes l
            JOIN users u ON u.telegram_id = l.from_user AND u.bot_instance = $2
            WHERE l.to_user = $1
            AND l.bot_instance = $2
            AND NOT EXISTS (
                SELECT 1 FROM matches m
                WHERE ((m.user1 = l.from_user AND m.user2 = l.to_user)
                OR (m.user1 = l.to_user AND m.user2 = l.from_user))
                AND m.bot_instance = $2
            )
            ORDER BY l.created_at DESC
        """, telegram_id, BOT_INSTANCE_ID)
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def accept_like(telegram_id, from_user):
    conn = await get_db()
    try:
        like = await conn.fetchrow(
            """SELECT id FROM likes 
               WHERE from_user = $1 AND to_user = $2 AND bot_instance = $3""",
            from_user, telegram_id, BOT_INSTANCE_ID
        )
        if not like:
            return None

        u1, u2 = min(from_user, telegram_id), max(from_user, telegram_id)
        row = await conn.fetchrow(
            """INSERT INTO matches (user1, user2, bot_instance) 
               VALUES ($1, $2, $3) ON CONFLICT DO NOTHING RETURNING id""",
            u1, u2, BOT_INSTANCE_ID
        )
        if not row:
            row = await conn.fetchrow(
                """SELECT id FROM matches 
                   WHERE user1 = $1 AND user2 = $2 AND bot_instance = $3""",
                u1, u2, BOT_INSTANCE_ID
            )
        return row['id'] if row else None
    finally:
        await conn.close()


async def reject_like(telegram_id, from_user):
    conn = await get_db()
    try:
        result = await conn.execute(
            """DELETE FROM likes 
               WHERE from_user = $1 AND to_user = $2 AND bot_instance = $3""",
            from_user, telegram_id, BOT_INSTANCE_ID
        )
        return result == 'DELETE 1'
    finally:
        await conn.close()


async def get_matches(telegram_id):
    conn = await get_db()
    try:
        rows = await conn.fetch("""
            SELECT m.id as match_id, m.created_at as matched_at,
                   u.telegram_id, u.username, u.full_name, u.gender, u.age, u.city,
                   u.interests, u.zodiac, u.goals, u.photo_file_id, u.photo_base64
            FROM matches m
            JOIN users u ON (
                CASE
                    WHEN m.user1 = $1 THEN m.user2 = u.telegram_id
                    ELSE m.user1 = u.telegram_id
                END
            )
            WHERE (m.user1 = $1 OR m.user2 = $1) AND m.bot_instance = $2
            ORDER BY m.created_at DESC
        """, telegram_id, BOT_INSTANCE_ID)
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def create_match(user1, user2):
    conn = await get_db()
    try:
        u1, u2 = min(user1, user2), max(user1, user2)
        row = await conn.fetchrow(
            """INSERT INTO matches (user1, user2, bot_instance) 
               VALUES ($1, $2, $3) ON CONFLICT DO NOTHING RETURNING id""",
            u1, u2, BOT_INSTANCE_ID
        )
        if not row:
            row = await conn.fetchrow(
                """SELECT id FROM matches 
                   WHERE user1 = $1 AND user2 = $2 AND bot_instance = $3""",
                u1, u2, BOT_INSTANCE_ID
            )
        return row['id'] if row else None
    finally:
        await conn.close()


async def get_chat_messages(match_id, limit=50):
    conn = await get_db()
    try:
        rows = await conn.fetch(
            """SELECT * FROM chat_messages 
               WHERE match_id = $1 AND bot_instance = $2 
               ORDER BY created_at DESC LIMIT $3""",
            match_id, BOT_INSTANCE_ID, limit
        )
        return [dict(r) for r in rows][::-1]
    finally:
        await conn.close()


async def send_chat_message(match_id, sender_id, message):
    conn = await get_db()
    try:
        await conn.execute(
            """INSERT INTO chat_messages (match_id, sender_id, message, bot_instance) 
               VALUES ($1, $2, $3, $4)""",
            match_id, sender_id, message, BOT_INSTANCE_ID
        )
        return True
    except Exception:
        return False
    finally:
        await conn.close()


async def mark_messages_read(match_id, reader_id):
    conn = await get_db()
    try:
        await conn.execute(
            """UPDATE chat_messages SET is_read = TRUE 
               WHERE match_id = $1 AND sender_id != $2 AND bot_instance = $3""",
            match_id, reader_id, BOT_INSTANCE_ID
        )
    finally:
        await conn.close()


# ========== GROUP FUNCTIONS ==========

async def get_group_invite_count(telegram_id):
    """Guruhga taklif qilinganlar sonini olish"""
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            """SELECT COUNT(*) as count FROM group_invites 
               WHERE inviter_id = $1 AND bot_instance = $2""",
            telegram_id, BOT_INSTANCE_ID
        )
        return row['count'] if row else 0
    finally:
        await conn.close()


async def get_group_invitees(telegram_id):
    """Guruhga taklif qilinganlar ro'yxatini olish"""
    conn = await get_db()
    try:
        rows = await conn.fetch("""
            SELECT u.telegram_id, u.full_name, u.username
            FROM group_invites gi
            JOIN users u ON u.telegram_id = gi.invited_id AND u.bot_instance = $2
            WHERE gi.inviter_id = $1 AND gi.bot_instance = $2
            ORDER BY gi.invited_at DESC
        """, telegram_id, BOT_INSTANCE_ID)
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def record_group_invite(inviter_id, invited_id):
    """Guruhga odam qo'shishni qayd etish"""
    conn = await get_db()
    try:
        await conn.execute("""
            INSERT INTO group_invites (inviter_id, invited_id, bot_instance)
            VALUES ($1, $2, $3)
            ON CONFLICT DO NOTHING
        """, inviter_id, invited_id, BOT_INSTANCE_ID)
        return True, "Guruhga odam qo'shildi."
    except Exception as e:
        return False, str(e)
    finally:
        await conn.close()


async def record_group_join(telegram_id, invited_by=None):
    """Guruhga a'zo bo'lishni qayd etish"""
    conn = await get_db()
    try:
        await conn.execute("""
            INSERT INTO group_members (telegram_id, invited_by, bot_instance)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO NOTHING
        """, telegram_id, invited_by, BOT_INSTANCE_ID)
    except Exception:
        pass
    finally:
        await conn.close()
