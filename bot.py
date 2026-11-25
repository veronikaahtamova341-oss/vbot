import os
import threading
import time
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

TOKEN = os.environ["VK_TOKEN"]
GROUP_ID = int(os.environ["VK_GROUP_ID"])

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

MENU = """Здесь можно выдохнуть. Что нужно сейчас?

• Дыхание — спокойная техника на 2 минуты
• Земля — вернуться в «здесь и сейчас»
• Выгорание — короткий тест
• Дневник — отметь своё состояние
• Поговорить — я просто выслушаю"""

CRISIS = ("Мне важно, что тебе сейчас тяжело. Пожалуйста, обратись к живому "
          "человеку: телефон доверия 8 (800) 2000-122 — бесплатно, круглосуточно. "
          "Ты не обязан(а) справляться в одиночку.")

CRISIS_WORDS = ("суицид", "самоубийств", "поконч", "не хочу жить",
                "не хочется жить", "умереть")

PORT = int(os.environ.get("PORT", 10000))  # Render сам подставит свой PORT


def send(user_id, text):
    vk.messages.send(user_id=user_id, message=text, random_id=get_random_id())


# --- крошечный веб-сервер, чтобы Render считал сервис живым ---
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass  # не засоряем логи пингами

def run_webserver():
    server = HTTPServer(("0.0.0.0", PORT), PingHandler)
    server.serve_forever()

def self_ping():
    # пингуем собственный URL каждые 10 минут, чтобы не заснуть
    url = os.environ.get("SELF_URL")  # например https://vk-bot-xxxx.onrender.com
    if not url:
        return
    while True:
        time.sleep(600)
        try:
            requests.get(url, timeout=10)
        except Exception as e:
            logging.warning("ping failed: %s", e)


# --- сам бот ---
def bot_loop():
    while True:  # автоперезапуск: если longpoll упал — начинаем заново
        try:
            for event in longpoll.listen():
                if event.type != VkBotEventType.MESSAGE_NEW:
                    continue
                user_id = event.obj.message["from_id"]
                text = (event.obj.message["text"] or "").lower().strip()

                if any(w in text for w in CRISIS_WORDS):
                    send(user_id, CRISIS)
                elif text in ("начать", ""):
                    send(user_id, f"Привет! Я — тихий уголок, где можно передохнуть.\n\n{MENU}")
                elif text == "дыхание":
                    send(user_id, "Давай замедлимся. 4 секунды вдох — задержка на 4 — "
                                  "выдох на 6.\n\nНачнём? (напиши «да», если готов)")
                elif text == "земля":
                    send(user_id, "Назови про себя:\n5 предметов, которые видишь\n"
                                  "4 звука, которые слышишь\n3 ощущения в теле\n"
                                  "2 запаха\n1 вещь, за которую ты благодарен себе сегодня.")
                elif text == "выгорание":
                    send(user_id, "Ответь числом от 1 до 5 на три вопроса:\n\n"
                                  "1. Насколько часто у тебя чувство опустошённости к вечеру?\n"
                                  "2. Насколько часто работа/учёба отнимает силы?\n"
                                  "3. Как часто ты не интересуешься тем, что раньше радовало?\n\n"
                                  "Сумма 12 и выше — сигнал отнестись к себе внимательнее. "
                                  "Это не диагноз, а повод для отдыха и разговора со специалистом.")
                elif text == "дневник":
                    send(user_id, "Как энергия сейчас — от 1 до 10? И одним словом: "
                                  "что вымотало больше всего?")
                elif text == "поговорить":
                    send(user_id, "Я рядом и слушаю. Расскажи, что происходит, — своими словами.")
                else:
                    send(user_id, f"Я понимаю тебя.\n\n{MENU}")
        except Exception as e:
            logging.exception("loop crashed: %s — restart in 10 sec", e)
            time.sleep(10)  # пауза, чтобы не молотить запросы при сбое ВК


if __name__ == "__main__":
    threading.Thread(target=run_webserver, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()
    bot_loop()
