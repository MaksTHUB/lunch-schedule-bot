import os
import requests
from datetime import date, timedelta

# День, с которого начинается цикл:
# ITGC = 12:00, АБИС = 12:30, KKZ = 13:00
START_DATE = date(2026, 2, 5)

TEAMS = ["ITGC", "АБИС", "KKZ"]
TIMES = ["12:00", "12:30", "13:00"]

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def is_workday(day):
    # Пн–Пт
    return day.weekday() < 5


def workdays_between(start, end):
    days = 0
    current = start

    while current <= end:
        if is_workday(current):
            days += 1
        current += timedelta(days=1)

    return days


def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        json={"chat_id": CHAT_ID, "text": text},
        timeout=20
    ).raise_for_status()


def main():
    today = date.today()

    # В выходные ничего не отправляем
    if not is_workday(today):
        return

    # Сколько рабочих дней прошло с начала
    day_number = workdays_between(START_DATE, today) - 1
    shift = day_number % 3

    # Сдвигаем время по кругу
    today_times = TIMES[shift:] + TIMES[:shift]

    message_lines = [
        f"{TEAMS[i]} - {today_times[i]}"
        for i in range(3)
    ]

    message = "🕘 Расписание обеда на сегодня:\n" + "\n".join(message_lines)
    send(message)


if __name__ == "__main__":
    main()