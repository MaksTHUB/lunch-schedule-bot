import os
import requests
from datetime import date, timedelta

# ДАТА СТАРТА ЦИКЛА:
# В эту дату (рабочий день) должно быть:
# Команда 1 = 12:00, Команда 2 = 12:30, Команда 3 = 13:00
CYCLE_START_DATE = date(2026, 2, 5)  # <-- поменяй на свою реальную дату старта

TEAMS = ["ITGC", "АБИС", "KKZ"]
TIMES = ["12:00", "12:30", "13:00"]  # базовый порядок для дня 0

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def is_workday(d: date) -> bool:
    # 0=Пн ... 4=Пт
    return d.weekday() < 5

def count_workdays(start: date, end: date) -> int:
    """Сколько рабочих дней прошло от start до end (start включительно, end включительно)."""
    step = 1 if end >= start else -1
    d = start
    count = 0
    while True:
        if is_workday(d):
            count += step
        if d == end:
            break
        d = d + timedelta(days=step)
    return count

def shift_times(shift: int) -> list[str]:
    # shift 0: [12:00, 12:30, 13:00]
    # shift 1: [12:30, 13:00, 12:00]
    # shift 2: [13:00, 12:00, 12:30]
    return TIMES[shift:] + TIMES[:shift]

def send_message(text: str) -> None:
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("Не заданы BOT_TOKEN или CHAT_ID в переменных окружения.")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=20)
    r.raise_for_status()

def main():
    today = date.today()

    # В выходные не отправляем (так ты и хотел: график 5/2)
    if not is_workday(today):
        return

    # Номер рабочего дня цикла:
    # В день старта count_workdays = 1 -> сделаем индекс 0
    workdays_from_start = count_workdays(CYCLE_START_DATE, today)
    idx = workdays_from_start - 1

    shift = idx % 3
    todays_times = shift_times(shift)

    lines = [f"{TEAMS[i]} - {todays_times[i]}" for i in range(3)]
    msg = "🕘 Расписание обеда на сегодня:\n" + "\n".join(lines)

    send_message(msg)

if __name__ == "__main__":
    main()
