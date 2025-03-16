import asyncio
import logging
from datetime import datetime, timedelta

import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, USER_IDS
from database import init_db, add_giveaway
from parsers import parse_giveaway_text
from scheduler import send_reminders
from telegram.constants import MessageOriginType

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Инициализация базы данных
init_db()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик входящих сообщений."""
    try:
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
        if forward_origin:
            if forward_origin.type == MessageOriginType.CHANNEL:
                channel_name = forward_origin.chat.title if forward_origin.chat else "Неизвестный канал"
                channel_link = f"@{forward_origin.chat.username}" if forward_origin.chat and forward_origin.chat.username else "Ссылка отсутствует"
            elif forward_origin.type == MessageOriginType.HIDDEN_USER:
                channel_name = "Скрытый пользователь"
                channel_link = "Ссылка отсутствует"
            else:
                channel_name = "Неизвестный источник"
                channel_link = "Ссылка отсутствует"
        else:
            channel_name = "Неизвестный источник"
            channel_link = "Ссылка отсутствует"

        giveaway_info = parse_giveaway_text(message_text)
        if giveaway_info:
            # Часовой пояс сервера (Франкфурт, UTC+2)
            server_timezone = pytz.timezone("Europe/Berlin")

            # Целевой часовой пояс (Москва, UTC+3)
            msk_timezone = pytz.timezone("Europe/Moscow")

            # Парсинг даты и времени из giveaway_info
            parsed_datetime = datetime.strptime(f"{giveaway_info['date']} {giveaway_info['time']}", "%Y-%m-%d %H:%M")
            msk_time = msk_timezone.localize(parsed_datetime)  # Локализация времени в МСК

            # Преобразование времени в часовой пояс сервера (Франкфурт)
            server_time = msk_time.astimezone(server_timezone)

            # Разница между Екатеринбургом (UTC+5) и Франкфуртом (UTC+2) — 3 часа
            ekb_offset = timedelta(hours=3)
            # Добавочные 2ч для вывода в сообщение правильного времени
            ekb_offset_output = timedelta(hours=1)
            adjusted_time = server_time + ekb_offset
            adjusted_time_output = adjusted_time + ekb_offset_output

            # Форматирование даты и времени для записи в БД
            adjusted_date = adjusted_time.strftime("%Y-%m-%d")
            adjusted_time_formatted = adjusted_time.strftime("%H:%M")
            # Время ТОЛЬКО для вывода сообщения
            adjusted_time_formatted_output = adjusted_time_output.strftime("%H:%M")

            # Запись времени в базу данных
            add_giveaway(user_id, channel_name, channel_link, adjusted_date, adjusted_time_formatted_output)

            response = (
                f"Розыгрыш с итогами {adjusted_date} {adjusted_time_formatted_output} (по Екб).\n"
                f"Канал: {channel_name} ({channel_link}).\nЗаписан в БД."
            )
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Не удалось найти информацию о розыгрыше. Проверьте текст сообщения.")
    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка при обработке сообщения.")


async def run_scheduler_background(bot_instance):
    """Фоновая задача для планировщика."""
    while True:
        try:
            logger.info("Запуск планировщика...")
            await send_reminders(bot_instance)
            logger.info("Планировщик завершил работу. Ожидание 60 секунд...")
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Ошибка в планировщике: {e}")
            await asyncio.sleep(30)  # меньший интервал при ошибке


async def post_init(application):
    """Выполняется после инициализации приложения."""
    bot_instance = application.bot
    application.create_task(run_scheduler_background(bot_instance))


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # Добавляем обработчик входящих сообщений
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, handle_message))

    logger.info("Бот запущен...")
    app.run_polling()
