import asyncio
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest
import re
from random import randint
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Конфигурация API
API_ID = 20010953  # Замените на ваш API ID
API_HASH = "5ffb40c12fbf7a782bab544f45e0d689"  # Замените на ваш API HASH

# Инициализация клиента Telethon
client = TelegramClient('session_name', API_ID, API_HASH)


# Случайная задержка для имитации человеческого поведения
def random_delay():
    delay = randint(3, 10)  # Задержка от 3 до 10 секунд
    logging.info(f"Задержка на {delay} секунд...")
    return delay


async def ensure_client_connected():
    """Убеждаемся, что клиент Telethon подключен."""
    if not client.is_connected():
        logging.info("Клиент Telethon отключен. Попытка подключения...")
        await client.connect()
        if not await client.is_user_authorized():
            logging.error("Клиент Telethon не авторизован. Проверьте API_ID и API_HASH.")
            raise Exception("Клиент Telethon не авторизован.")


async def handle_raffle(message_text, user_id, send_reply, channel_usernames):
    """
    Обработка розыгрыша: подписка на каналы.
    :param message_text: Текст сообщения с розыгрышем.
    :param user_id: ID пользователя, которому отправлять ответы.
    :param send_reply: Функция для отправки ответов пользователю.
    :param channel_usernames: Список каналов для подписки.
    """
    try:
        # Убедимся, что клиент подключен
        await ensure_client_connected()

        if not channel_usernames:
            logging.warning("Не удалось найти каналы для подписки.")
            await send_reply("Не удалось найти каналы для подписки.")
            return

        logging.info(f"Найдены каналы: {', '.join(channel_usernames)}")

        # Подписываемся на каждый канал
        failed_channels = []
        for channel_username in channel_usernames:
            try:
                logging.info(f"Попытка подписаться на канал @{channel_username} ...")
                await asyncio.sleep(random_delay())  # Задержка перед подпиской
                await client(JoinChannelRequest(channel_username))
                logging.info(f"Успешно подписались на канал @{channel_username}.")
                await send_reply(f"Успешно подписались на канал @{channel_username}.")
            except UserAlreadyParticipantError:
                logging.info(f"Уже подписаны на канал @{channel_username}.")
                await send_reply(f"Вы уже подписаны на канал @{channel_username}.")
            except Exception as e:
                logging.error(f"Не удалось подписаться на канал @{channel_username}: {e}")
                failed_channels.append(channel_username)

        # Отправляем итоговое сообщение
        if failed_channels:
            failed_channels_str = ', '.join([f'@{ch}' for ch in failed_channels])
            await send_reply(f"Не удалось подписаться на канал(ы): {failed_channels_str}.")
        else:
            await send_reply("Успешно подписаны на все каналы. Нажмите кнопку участвовать.")

    except FloodWaitError as e:
        logging.error(f"Обнаружена блокировка FloodWait: ждём {e.seconds} секунд.")
        await asyncio.sleep(e.seconds)
        await send_reply("Обнаружена временная блокировка. Попробуйте позже.")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        await send_reply("Что-то пошло не так. Нужно попробовать вручную.")


async def start_telethon():
    """Запуск клиента Telethon."""
    await client.start()
    logging.info("Клиент Telethon успешно запущен.")
    await client.run_until_disconnected()
