import logging
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, USER_IDS
from database import init_db, add_giveaway
from parsers import parse_giveaway_text
from scheduler import run_scheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Инициализация базы данных
init_db()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик входящих сообщений."""
    user_id = update.message.from_user.id
    if user_id not in USER_IDS:
        await update.message.reply_text("У вас нет доступа к этому боту.")
        return

    message_text = update.message.text or update.message.caption or ""
    if not message_text.strip():
        await update.message.reply_text("Сообщение пустое или не содержит текста.")
        return

    # Получаем данные о пересланном сообщении
    forward_origin = update.message.forward_origin
    channel_name = forward_origin.chat.title if forward_origin and forward_origin.type == "channel" else "Неизвестный канал"
    channel_link = f"@{forward_origin.chat.username}" if forward_origin and forward_origin.chat.username else "Ссылка отсутствует"

    giveaway_info = parse_giveaway_text(message_text)
    if giveaway_info:
        add_giveaway(user_id, channel_name, channel_link, giveaway_info["date"], giveaway_info["time"])
        response = (
            f"Розыгрыш с итогами {giveaway_info['date']} {giveaway_info['time']}.\n"
            f"Канал: {channel_name} ({channel_link}).\nЗаписан в БД."
        )
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Не удалось найти информацию о розыгрыше. Проверьте текст сообщения.")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчик входящих сообщений
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, handle_message))

    # Запускаем планировщик в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler, args=(app.bot,))
    scheduler_thread.daemon = True
    scheduler_thread.start()

    logger.info("Бот запущен...")
    app.run_polling()
