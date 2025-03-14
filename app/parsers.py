import re
from datetime import datetime
from handler_auto import logger
import dateparser


def parse_giveaway_text(text):
    """Анализ текста для извлечения даты и времени."""
    date_time_patterns = [
        r"(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})\s*в\s*(\d{1,2}:\d{2})",  # 24.03.2025 в 19:00
        r"(\d{1,2}\s*[а-я]+\s*\d{2,4})\s*в\s*(\d{1,2}:\d{2})",  # 24 марта 2025 в 19:00
        r"(\d{1,2}\s*[а-я]+)\s*в\s*(\d{1,2}:\d{2})",  # 24 марта в 19:00
        r"(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})\s+(\d{1,2}:\d{2})",  # 24.03.2025 19:00
        r"(\d{1,2}\s*[а-я]+\s*\d{2,4})\s+(\d{1,2}:\d{2})",  # 24 марта 2025 19:00
        r"(\d{1,2}\s*[а-я]+)\s+(\d{1,2}:\d{2})",  # 24 марта 19:00
        r"(\d{1,2}:\d{2}),\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",  # 19:00, 24.03.2025
        r"(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",  # 24.03.2025
        r"(\d{1,2}\s*[а-я]+\s*\d{2,4})",  # 24 марта 2025
        r"(\d{1,2}\s*[а-я]+)",  # 24 марта
        r"(\d{1,2}\s*[а-я].)",  # 24 марта.
        r"(\d{1,2}\s*[а-я]+),\s*в\s*(\d{1,2}:\d{2})",  # 20 марта, в 14:00
        r"(\d{1,2}\s*[а-я]+)\s*,\s*(\d{1,2}:\d{2})",  # 20 марта, 14:00
        r"(\d{1,2}\s*[а-я]+)\s*-\s*(\d{1,2}:\d{2})",  # 20 марта - 14:00
        r"(\d{1,2}\s*[а-я]+)\s+в\s+(\d{1,2}:\d{2})",  # 20 марта в 14:00 (без запятой)
        r"(\d{1,2}[.\-/]\d{1,2})\s*в\s*(\d{1,2}:\d{2})",  # 31.03 в 19:00
        r"(\d{1,2}[.\-/]\d{1,2}),\s*(\d{1,2}:\d{2})",  # 31.03, 19:00
    ]

    for pattern in date_time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw_date = match.group(1)
            raw_time = match.group(2) if len(match.groups()) > 1 else None

            parsed_date = dateparser.parse(raw_date, settings={'DATE_ORDER': 'DMY'})
            if parsed_date:
                date = parsed_date.strftime("%Y-%m-%d")
                time = raw_time
                if time is not None:
                    try:
                        datetime.strptime(time, "%H:%M")
                    except ValueError:
                        time = "18:00"
                else:
                    time = "18:00"
                logger.info(f"date: {date}, time: {time}")
                return {"date": date, "time": time}

    # # Попытка найти дату без времени
    # parsed_date = dateparser.parse(text, settings={'DATE_ORDER': 'DMY'})
    # if parsed_date:
    #     date = parsed_date.strftime("%Y-%m-%d")
    #     logger.info(f"date: {date}")
    #     time = "18:00"  # Устанавливаем дефолтное время
    #     logger.info(f"time: {time}")
    #     return {"date": date, "time": time}

    # return None
