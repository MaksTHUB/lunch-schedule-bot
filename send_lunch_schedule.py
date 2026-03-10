import os
import requests
from datetime import date, timedelta

# День старта цикла:
# ITGC = 12:00, АБИС = 12:30, KKZ = 13:00
START_DATE = date(2026, 2, 5)

TEAMS = ["ITGC", "АБИС", "KKZ"]
TIMES = ["12:00", "12:30", "13:00"]

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


def is_workday(day):
    # Сб и Вс
    if day.weekday() >= 5:
        return False
    # Дополнительные выходные
    if day in HOLIDAYS:
        return False
    return True


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

    # В выходные и праздники ничего не отправляем
    if not is_workday(today):
        return

    # Сколько рабочих дней прошло с даты старта
    day_number = workdays_between(START_DATE, today) - 1
    shift = day_number % 3

    # Сдвигаем время по кругу
    today_times = TIMES[shift:] + TIMES[:shift]

    lines = [
        f"{TEAMS[i]} - {today_times[i]}"
        for i in range(3)
    ]

    message = "🕘 Расписание обеда на сегодня:\n" + "\n".join(lines)
    send(message)


if __name__ == "__main__":
    main()
