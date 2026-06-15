import os

# ========== BOT INSTANCE ISOLATION ==========
# HAR BIR BOT UCHUN ALohida sozlamalar!
# 
# 1-bot uchun Railway Environment Variables:
#   BOT_INSTANCE_ID=bot1
#   BOT_TOKEN=token1
#   DATABASE_URL=postgresql://.../bot1_db
#   WEBAPP_URL=https://user1.github.io/bot1/
#   API_BASE_URL=https://bot1-backend.up.railway.app
#   ADMIN_PASSWORD=pass1
#   GROUP_CHAT_ID=-100...
#   GROUP_INVITE_LINK=https://t.me/...
#
# 2-bot uchun Railway Environment Variables:
#   BOT_INSTANCE_ID=bot2
#   BOT_TOKEN=token2
#   DATABASE_URL=postgresql://.../bot2_db
#   WEBAPP_URL=https://user2.github.io/bot2/
#   API_BASE_URL=https://bot2-backend.up.railway.app
#   ADMIN_PASSWORD=pass2
#   GROUP_CHAT_ID=-100...
#   GROUP_INVITE_LINK=https://t.me/...
# ===========================================

BOT_INSTANCE_ID = os.getenv("BOT_INSTANCE_ID", "default")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8647959441:AAFZ-8CaYu-gH0lNoWa9w_TVx4eXyrSHqrk")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:vlePdKdpwQhQyVTMjOsdMLfluFGGHaJM@thomas.proxy.rlwy.net:43373/railway")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://asliddinx278-ops.github.io/88/")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "dtudrdudrdrturtrur")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1003097266971")) if os.getenv("GROUP_CHAT_ID") else None
GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK", "https://t.me/asssssssslw")

# API Base URL - backend server URL (WEBAPP_URL dan farqli!)
# Har bir bot o'zining alohida Railway backend'iga ulanadi
API_BASE_URL = os.getenv("API_BASE_URL", WEBAPP_URL)

# Validate critical configuration
if not BOT_TOKEN:
    raise ValueError(f"[{BOT_INSTANCE_ID}] BOT_TOKEN sozlanmagan! Railway'da BOT_TOKEN environment variable qo'shing.")
if not DATABASE_URL:
    raise ValueError(f"[{BOT_INSTANCE_ID}] DATABASE_URL sozlanmagan! Har bir bot uchun alohida PostgreSQL database yarating.")
if not WEBAPP_URL:
    raise ValueError(f"[{BOT_INSTANCE_ID}] WEBAPP_URL sozlanmagan! Har bir bot uchun alohida WebApp URL kerak.")
