import re
import random
import asyncio
from datetime import datetime

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, UserAlreadyParticipantError
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.tl.functions.channels import JoinChannelRequest
from config import API_ID, API_HASH, ADMIN_CHAT_ID
import logging
from database import add_giveaway

# Создание клиента Telethon
client = TelegramClient("raffle_participant", API_ID, API_HASH)

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Функция случайной задержки для имитации человеческого поведения
async def random_delay():
    """Случайная задержка от 1 до 5 минут."""
    delay = random.randint(300, 1800)
    logger.info(f"Задержка перед следующим действием: {delay} секунд.")
    await asyncio.sleep(delay)


# Функция для подписки на канал
async def join_channel(channel_username):
    """Подписка на канал."""
    try:
        await client(JoinChannelRequest(channel_username))
        logger.info(f"Успешно подписан на канал @{channel_username}")
        return True
    except FloodWaitError as e:
        logger.warning(f"Слишком много запросов. Ожидание {e.seconds} секунд.")
        await asyncio.sleep(e.seconds)
        return False
    except UserAlreadyParticipantError:
        logger.info(f"Уже подписан на канал @{channel_username}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при подписке на канал @{channel_username}: {e}")
        return False


# Функция для нажатия на кнопку
async def press_button(channel_entity, message_id, button_data):
    """Нажатие на кнопку 'участвую'."""
    try:
        await client(GetBotCallbackAnswerRequest(
            peer=channel_entity,
            msg_id=message_id,
            data=button_data
        ))
        logger.info(f"Успешно нажата кнопка на канале {channel_entity.username}")

        # Сохраняем информацию в базу данных
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%Y-%m-%d")
        add_giveaway(
            user_id=ADMIN_CHAT_ID,
            channel_name=channel_entity.username,
            channel_link=f"@{channel_entity.username}",
            date=current_date,
            time=current_time
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка при нажатии кнопки на канале {channel_entity.username}: {e}")
        return False


# Обработка нового сообщения
@client.on(events.NewMessage(chats="raffleblog"))
async def handle_new_message(event):
    """Обработка новых сообщений из канала @raffleblog."""
    message = event.message
    text = message.text or message.caption or ""
    logger.info(f"Новое сообщение в канале @raffleblog: {text}")

    # Поиск ссылок на каналы
    channel_links = re.findall(r"https://t\.me/(\w+)", text) + re.findall(r"@(\w+)", text)

    # Поиск кнопок
    buttons = []
    if message.buttons:
        for row in message.buttons:
            for button in row:
                if button.text and "участвую" in button.text.lower():
                    buttons.append((button.text, button.data))

    # Подписываемся на каналы
    for channel_username in channel_links:
        success = await join_channel(channel_username)
        if not success:
            await client.send_message(ADMIN_CHAT_ID,
                                      f"Не удалось подписаться на канал @{channel_username}. Требуется участие вручную.")

    # Нажимаем на кнопки
    for button_text, button_data in buttons:
        success = await press_button(message.peer_id, message.id, button_data)
        if success:
            await client.send_message(ADMIN_CHAT_ID, f"Успешно принято участие на канале {message.chat.username}.")
        else:
            await client.send_message(ADMIN_CHAT_ID,
                                      f"Не удалось принять участие на канале {message.chat.username}. Требуется участие вручную.")

    # Добавляем случайную задержку
    await random_delay()


# Запуск клиента
async def run_auto_handler():
    """Запуск автоматического обработчика."""
    logger.info("Запуск клиента Telethon...")
    await client.start()
    logger.info("Клиент запущен. Мониторинг канала @raffleblog...")
    await client.run_until_disconnected()
