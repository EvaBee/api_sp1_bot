import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
bot = Bot(token=TELEGRAM_TOKEN)
verdict_statuses = {
    "reviewing": None,
    "approved": "Ревьюеру всё понравилось, работа зачтена!",
    "rejected": "К сожалению, в работе нашлись ошибки."
}


def parse_homework_status(homework):
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    if homework_status is None or homework_status not in verdict_statuses:
        logging.error(
            f'Яндекс Практикум вернул неожиданный ответ: {homework_status}')
    verdict = verdict_statuses[homework_status]
    if not verdict:
        return f'Работа {homework_name} взята в ревью'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {"from_date": current_timestamp}
    try:
        homework_statuses = requests.get(URL, params=params, headers=headers)
        return homework_statuses.json()
    except requests.exceptions.RequestException:
        logging.exception("Возникла ошибка при соединении с сервером")
        raise


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homeworks(current_timestamp)
            if new_homework.get("homeworks"):
                send_message(
                    parse_homework_status(new_homework.get("homeworks")[0]))
            current_timestamp = new_homework.get(
                "current_date")  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут
        except Exception as e:
            logging.error(e)
            send_message(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == "__main__":
    main()
