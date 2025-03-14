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
client = TelegramClient("raffle_participant", API_ID, API_HASH, connection_retries=5)

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def random_delay(min_seconds=300, max_seconds=1800):
    """Случайная задержка с дополнительной вариативностью."""
    delay = random.randint(min_seconds, max_seconds)
    logger.info(f"Задержка перед следующим действием: {delay} секунд.")
    await asyncio.sleep(delay)

    if random.random() < 0.3:  # 30% шанс добавить еще одну короткую задержку
        extra_delay = random.randint(10, 60)
        logger.info(f"Дополнительная задержка: {extra_delay} секунд.")
        await asyncio.sleep(extra_delay)


async def join_channel(channel_username):
    """Подписка на канал с учетом FloodWaitError."""
    try:
        await client(JoinChannelRequest(channel_username))
        logger.info(f"Успешно подписан на канал @{channel_username}")
        return True
    except FloodWaitError as e:
        wait_time = e.seconds + random.randint(60, 300)
        logger.warning(f"Слишком много запросов. Ожидание {wait_time} секунд.")
        await asyncio.sleep(wait_time)
        return False
    except UserAlreadyParticipantError:
        logger.info(f"Уже подписан на канал @{channel_username}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при подписке на канал @{channel_username}: {e}")
        return False


async def press_button(channel_entity, message_id, button_data):
    """Нажатие на кнопку с учетом возможных ошибок."""
    try:
        await client(GetBotCallbackAnswerRequest(
            peer=channel_entity,
            msg_id=message_id,
            data=button_data
        ))
        logger.info(f"Успешно нажата кнопка на канале {channel_entity.username}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при нажатии кнопки на канале {channel_entity.username}: {e}")
        return False


@client.on(events.NewMessage(chats=["raffleblog", "giveawayschannel"]))
async def handle_new_message(event):
    """Обработка новых сообщений из каналов."""
    message = event.message
    text = message.text or message.caption or ""

    if not is_giveaway_message(text):
        logger.info("Сообщение не связано с розыгрышем. Пропускаем.")
        return

    logger.info(f"Новое сообщение: {text}")

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


def is_giveaway_message(text):
    """Проверка, является ли сообщение розыгрышем."""
    giveaway_keywords = [
        "розыгрыш", "Розыгрыш", "Приз", "конкурс", "приз", "участвуй", "победитель", "подпишись", "лайк",
        "подписаться", "вступить", "comment", "комментарий", "share", "поделиться"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in giveaway_keywords)


async def run_auto_handler():
    """Запуск автоматического обработчика."""
    logger.info("Запуск клиента Telethon...")
    await client.start()
    logger.info("Клиент запущен. Мониторинг каналов...")
    await client.run_until_disconnected()
