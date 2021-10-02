import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot


load_dotenv()

PRAKTIСUM_TOKEN = os.getenv("TOKEND")
TELEGRAM_TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
chat_id = CHAT_ID
bot = Bot(token=TELEGRAM_TOKEN)
url = "https://practicum.yandex.ru/api/user_api/homework_statuses/"


def parse_homework_status(homework):
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    if homework_status not in ("approved", "rejected"):
        verdict = "работа взята в ревью"
    elif homework_status == "rejected":
        verdict = "К сожалению, в работе нашлись ошибки."
    else:
        verdict = "Ревьюеру всё понравилось, работа зачтена!"
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {"Authorization": f"OAuth {PRAKTIСUM_TOKEN}"}
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
    current_timestamp = 12000

    while True:
        try:
            new_homework = get_homeworks(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get(
                'current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут
        except Exception as e:
            print(f"Бот упал с ошибкой: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
