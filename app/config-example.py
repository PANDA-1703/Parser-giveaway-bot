import os

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR-TOKEN")
USER_IDS = list(map(int, os.getenv("USER_IDS", "YOUR-TG-ID").split(",")))

# Настройки базы данных
DB_NAME = "giveaways.db"

# Логирование
LOG_LEVEL = "INFO"

# Настройки API
API_ID = "YOUR_API-ID"  # type: int
API_HASH = "YOUR-API-HASH"
SESSION_NAME = "raffle_participant"
ADMIN_CHAT_ID = "YOUR-TG-ID"    # type: int
