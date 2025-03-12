import os

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "XXXX")
USER_IDS = list(map(int, os.getenv("USER_IDS", "0000,0000,0000").split(",")))

# Настройки базы данных
DB_NAME = "giveaways.db"

# Логирование
LOG_LEVEL = "INFO"