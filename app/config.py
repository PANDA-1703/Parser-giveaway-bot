import os

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "7688923038:AAE3eiyW5x68LQrZWfZRix2hEfVcErF2HDY")
USER_IDS = list(map(int, os.getenv("USER_IDS", "585058267,7539413707,8062709641").split(",")))

# Настройки базы данных
DB_NAME = "giveaways.db"

# Логирование
LOG_LEVEL = "INFO"