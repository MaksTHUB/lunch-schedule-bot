import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests


# Новая точка начала цикла:
# 29.07.2026:
# ITGC — 13:00
# АБИС — 12:00
# KKZ — 12:30
START_DATE = date(2026, 7, 29)

TEAMS = ["ITGC", "АБИС", "KKZ"]
START_TIMES = ["13:00", "12:00", "12:30"]

ALMATY_TIMEZONE = ZoneInfo("Asia/Almaty")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# Дополнительные выходные дни в 2026 году
HOLIDAYS = {
    date(2026, 3, 9),
    date(2026, 3, 23),
    date(2026, 3, 24),
    date(2026, 3, 25),
    date(2026, 5, 1),
    date(2026, 5, 7),
    date(2026, 5, 11),
    date(2026, 5, 27),
    date(2026, 7, 6),
    date(2026, 8, 31),
    date(2026, 10, 26),
    date(2026, 12, 16),
}


def is_workday(day: date) -> bool:
    """Проверяет, является ли дата рабочим днём."""

    # Суббота или воскресенье
    if day.weekday() >= 5:
        return False

    # Дополнительный выходной
    if day in HOLIDAYS:
        return False

    return True


def count_workdays(start: date, end: date) -> int:
    """
    Считает рабочие дни от start включительно,
    но не включает end.
    """

    if end < start:
        raise ValueError("Текущая дата не может быть раньше START_DATE")

    days = 0
    current = start

    while current < end:
        if is_workday(current):
            days += 1

        current += timedelta(days=1)

    return days


def send_message(text: str) -> None:
    """Отправляет сообщение в Telegram."""

    if not BOT_TOKEN:
        raise RuntimeError("Не задан GitHub Secret BOT_TOKEN")

    if not CHAT_ID:
        raise RuntimeError("Не задан GitHub Secret CHAT_ID")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text,
        },
        timeout=20,
    )

    response.raise_for_status()


def main() -> None:
    # Используем именно дату Алматы, а не UTC-даты GitHub Runner
    today = datetime.now(ALMATY_TIMEZONE).date()

    # В выходные и праздники ничего не отправляем
    if not is_workday(today):
        print(f"{today}: выходной день, сообщение не отправлено")
        return

    # Количество рабочих дней после START_DATE
    day_number = count_workdays(START_DATE, today)

    # Сдвиг расписания: 0 → 1 → 2 → 0
    shift = day_number % len(TEAMS)

    today_times = START_TIMES[shift:] + START_TIMES[:shift]

    lines = [
        f"{team} - {lunch_time}"
        for team, lunch_time in zip(TEAMS, today_times)
    ]

    message = (
        "🕘 Расписание обеда на сегодня:\n"
        + "\n".join(lines)
    )

    print(message)
    send_message(message)


if __name__ == "__main__":
    main()
