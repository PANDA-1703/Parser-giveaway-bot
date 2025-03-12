import re
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
    ]

    for pattern in date_time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw_date = match.group(1)
            raw_time = match.group(2) if len(match.groups()) > 1 else None

            parsed_date = dateparser.parse(raw_date, settings={'DATE_ORDER': 'DMY'})
            if parsed_date:
                date = parsed_date.strftime("%Y-%m-%d")
                time = raw_time or "Не указано"
                return {"date": date, "time": time}

    parsed_date = dateparser.parse(text, settings={'DATE_ORDER': 'DMY'})
    if parsed_date:
        date = parsed_date.strftime("%Y-%m-%d")
        time = parsed_date.strftime("%H:%M") if parsed_date.hour != 0 and parsed_date.minute != 0 else "Не указано"
        return {"date": date, "time": time}

    return None
