import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("TOKEND")
TELEGRAM_TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
chat_id = CHAT_ID
bot = Bot(token=TELEGRAM_TOKEN)
url = "https://practicum.yandex.ru/api/user_api/homework_statuses/"


def parse_homework_status(homework):
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    if homework_status == "reviewing":
        verdict = "работа взята в ревью"
    elif homework_status == "rejected":
        verdict = "К сожалению, в работе нашлись ошибки."
    else:
        verdict = "Ревьюеру всё понравилось, работа зачтена!"
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, params=params, headers=headers)
        return homework_statuses.json()
    except Exception as e:
        logging.exception(f'error {e}')
        return {}


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = 1622622666

    while True:
        try:
            print(1)
            send_message(
                parse_homework_status(get_homeworks(current_timestamp)))
            time.sleep(300)
        except Exception as e:
            print(f"Бот упал с ошибкой: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
