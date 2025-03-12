import time
from datetime import datetime, timedelta
import pytz
from telegram import Bot
from database import get_todays_giveaways


def send_reminders(bot_instance):
    """
    Отправка напоминаний о розыгрышах с учётом часового пояса.
    :param bot_instance: Экземпляр бота Telegram.
    """
    # Установка временной зоны МСК
    msk_timezone = pytz.timezone("Europe/Moscow")
    now_msk = datetime.now(msk_timezone)

    # Добавляем +1 час к текущему времени
    your_timezone_time = now_msk + timedelta(hours=1)
    current_date = your_timezone_time.strftime("%Y-%m-%d")
    current_time = your_timezone_time.strftime("%H:%M")

    giveaways = get_todays_giveaways(current_date, current_time)
    for user_id, channel_name in giveaways:
        try:
            bot_instance.send_message(
                chat_id=user_id,
                text=f"Сейчас будут подводиться итоги розыгрыша на канале {channel_name}!"
            )
        except Exception as e:
            print(f"Ошибка при отправке напоминания пользователю {user_id}: {e}")


def run_scheduler(bot_instance):
    """
    Запуск планировщика задач.
    :param bot_instance: Экземпляр бота Telegram.
    """
    while True:
        send_reminders(bot_instance)
        time.sleep(60)