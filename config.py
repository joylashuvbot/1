import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://anketabot.github.io/tanishuvweb/")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "LoveBot!2026!StrongPass")

# Guruh sozlamalari
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1003888172359")) if os.getenv("GROUP_CHAT_ID") else None
GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK", "https://t.me/+HA4J8P7lht0zZTdi")