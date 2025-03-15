import asyncio
import logging
import re
from datetime import datetime, timedelta

import pytz
from telegram import Update
from telegram.constants import MessageOriginType
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, USER_IDS
from database import init_db, add_giveaway
from parsers import parse_giveaway_text
from scheduler import send_reminders
from telethon_handler import handle_raffle, start_telethon

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Инициализация базы данных
init_db()


async def send_reply(bot_instance, user_id, message):
    """
    Отправка ответа пользователю через python-telegram-bot.
    :param bot_instance: Экземпляр бота Telegram.
    :param user_id: ID пользователя, которому отправлять сообщение.
    :param message: Текст сообщения.
    """
    try:
        await bot_instance.send_message(chat_id=user_id, text=message)
        logging.info(f"Отправлено сообщение пользователю {user_id}: {message}")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")


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
        channel_name = "Неизвестный источник"
        channel_link = "Ссылка отсутствует"

        if forward_origin:
            if forward_origin.type == MessageOriginType.CHANNEL:
                channel_name = forward_origin.chat.title if forward_origin.chat else "Неизвестный канал"
                channel_link = f"@{forward_origin.chat.username}" if forward_origin.chat and forward_origin.chat.username else "Ссылка отсутствует"
            elif forward_origin.type == MessageOriginType.HIDDEN_USER:
                channel_name = "Скрытый пользователь"
                channel_link = "Ссылка отсутствует"

        entities = update.message.entities or []
        channel_usernames = []

        # Шаг 1: Ищем ссылки в тексте (явные и через гиперссылки)
        if message_text.strip():
            channel_usernames = re.findall(r'(?:https?://t\.me/|@)([\w_]+)', message_text)

            for entity in entities:
                if entity.type == "text_link":
                    url = entity.url
                    match = re.search(r'(?:https?://t\.me/|@)([\w_]+)', url)
                    if match:
                        channel_usernames.append(match.group(1))

        # Если ссылки не найдены, используем данные о пересланном сообщении
        if not channel_usernames:
            if forward_origin and forward_origin.type == "channel":
                channel_username = forward_origin.chat.username
                if channel_username:
                    channel_usernames = [channel_username]
                    logging.info(f"Сообщение переслано из канала @{channel_username}.")
                else:
                    logging.warning("Не удалось найти username канала, от которого переслано сообщение.")
                    await update.message.reply_text("Не удалось найти ссылки на каналы для подписки. Подпишитесь вручную.")
                    return
            else:
                logging.warning("Не удалось найти ссылки на каналы в тексте и сообщение не переслано из канала.")
                await update.message.reply_text("Не удалось найти ссылки на каналы в тексте и сообщение не переслано из канала.")
                return

        # Удаляем дубликаты каналов
        channel_usernames = list(set(channel_usernames))

        # Шаг 2: Подписываемся на каналы через Telethon
        await handle_raffle(
            message_text,
            user_id,
            lambda msg: send_reply(context.bot, user_id, msg),
            channel_usernames
        )

        # Шаг 3: Парсим дату и время розыгрыша
        giveaway_info = parse_giveaway_text(message_text)
        if giveaway_info:
            # Часовой пояс сервера (Франкфурт, UTC+2)
            server_timezone = pytz.timezone("Europe/Berlin")
            msk_timezone = pytz.timezone("Europe/Moscow")

            parsed_datetime = datetime.strptime(f"{giveaway_info['date']} {giveaway_info['time']}", "%Y-%m-%d %H:%M")
            msk_time = msk_timezone.localize(parsed_datetime)
            server_time = msk_time.astimezone(server_timezone)

            ekb_offset = timedelta(hours=3)
            ekb_offset_output = timedelta(hours=1)
            adjusted_time = server_time + ekb_offset
            adjusted_time_output = adjusted_time + ekb_offset_output

            adjusted_date = adjusted_time.strftime("%Y-%m-%d")
            adjusted_time_formatted = adjusted_time.strftime("%H:%M")
            adjusted_time_formatted_output = adjusted_time_output.strftime("%H:%M")

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
        logger.info("Запуск планировщика...")
        await send_reminders(bot_instance)
        logger.info("Планировщик завершил работу. Ожидание 60 секунд...")
        await asyncio.sleep(60)


async def post_init(application):
    """Выполняется после инициализации приложения."""
    bot_instance = application.bot
    application.create_task(run_scheduler_background(bot_instance))

    # Запускаем клиент Telethon как фоновую задачу
    application.create_task(start_telethon())


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # Добавляем обработчик входящих сообщений
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, handle_message))

    logger.info("Бот запущен...")
    app.run_polling()

    # Корректное завершение работы
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(app.stop())
    finally:
        loop.close()