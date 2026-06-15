import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8647959441:AAFZ-8CaYu-gH0lNoWa9w_TVx4eXyrSHqrk")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:vlePdKdpwQhQyVTMjOsdMLfluFGGHaJM@thomas.proxy.rlwy.net:43373/railway")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://asliddinx278-ops.github.io/88/")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "LoveBot!2026!StrongPass")

# Guruh sozlamalari
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1003097266971")) if os.getenv("GROUP_CHAT_ID") else None
GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK", "https://t.me/asssssssslw")
