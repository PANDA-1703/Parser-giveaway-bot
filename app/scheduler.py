import asyncio
from datetime import datetime, timedelta
import pytz

from database import get_todays_giveaways, delete_sendler_giveaways
import logging


async def send_reminders(bot_instance):
    """
    Отправка напоминаний о розыгрышах с учётом часового пояса.
    :param bot_instance: Экземпляр бота Telegram.
    """
    # Текущее время в часовом поясе Екатеринбурга
    ekb_timezone = pytz.timezone("Asia/Yekaterinburg")
    now_ekb = datetime.now(ekb_timezone)

    # Форматирование даты и времени для Екатеринбурга
    current_date = now_ekb.strftime("%Y-%m-%d")
    current_time = now_ekb.strftime("%H:%M")

    # Получение розыгрышей на текущую дату и время
    giveaways = get_todays_giveaways(current_date, current_time)
    for giveaway_id, user_id, channel_name, channel_link in giveaways:
        try:
            await bot_instance.send_message(
                chat_id=user_id,
                text=f"Проверь итоги розыгрыша на канале {channel_name} ({channel_link})!"
            )
            # Удаление отправленной записи
            delete_sendler_giveaways(giveaway_id)
        except Exception as e:
            logging.error(f"Ошибка при отправке напоминания пользователю {user_id}: {e}")
