import os

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "7688923038:AAE3eiyW5x68LQrZWfZRix2hEfVcErF2HDY")
USER_IDS = list(map(int, os.getenv("USER_IDS", "585058267,7539413707,8062709641,1286453715,7893293544").split(",")))

# Настройки базы данных
DB_NAME = "giveaways.db"

# Логирование
LOG_LEVEL = "INFO"

# Настройки API
API_ID = 20010953
API_HASH = "5ffb40c12fbf7a782bab544f45e0d689"
SESSION_NAME = "raffle_participant"
ADMIN_CHAT_ID = 585058267