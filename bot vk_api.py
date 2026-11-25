import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

TOKEN = "vk1.a.h0wcyRe20jXgnSdNvX0BUbn1o4vi_2oA24z8J4YgKtCQO4cP4Vz3WbEY0vASXyltno-967iy0Of1nUAiUMeY_EOZ6X4lCahiB5BkHzO0vSRDpbjcJ_vFPJUNh0b0Ac-FjrHXlfaXrlHwPYhVhoDgy6-_-AEQW1F5S19BgZa5Lr5JahtqkVoSjlogeJGSeoKgHSBwQDn8D1_rvkc3Szv59Q"
GROUP_ID = 243590130 

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

MENU = """Здесь можно выдохнуть. Что нужно сейчас?

• Дыхание — спокойная техника на 2 минуты
• Земля — вернуться в «здесь и сейчас»
• Выгорание — короткий тест
• Дневник — отметь своё состояние
• Поговорить — я просто выслушаю"""

def send(user_id, text):
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=get_random_id(),
    )

CRISIS = ("Мне важно, что вам сейчас тяжело. Пожалуйста, обратитесь к живому "
          "человеку: телефон доверия 8 (800) 2000-122 "
          "(бесплатно,круглосуточно).Вы не обязаны справляться в одиночку.")

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.obj.message["from_id"]
        text = (event.obj.message["text"] or "").lower().strip()

        if text == "начать" or not text:
            send(user_id, f"Привет! Я — тихий уголок, где можно передохнуть.\n\n{MENU}")
        elif any(w in text for w in ("суицид", "не хочу жить", "умереть", "самоубийство")):
            send(user_id, CRISIS)
        elif text == "дыхание":
            send(user_id, "Давай замедлимся. 4 секунды вдох — задержка на 4 — "
                          "выдох на 6. Я напишу «и» в темпе, а ты дыши.\n\n"
                          "Начнём? (напиши «да», если готов)")
        elif text == "земля":
            send(user_id, "Назови про себя:\n5 предметов, которые видишь\n"
                          "4 звука, которые слышишь\n3 ощущения в теле\n"
                          "2 запаха\n1 вещь, за которую ты благодарен себе сегодня.")
        elif text == "выгорание":
            send(user_id, "Ответь числом от 1 до 5 на три вопроса:\n\n"
                          "1. Насколько часто у тебя чувство опустошённости к вечеру?\n"
                          "2. Насколько часто работа/учёба отнимает силы, не оставляя ничего?\n"
                          "3. Как часто ты чувствуешь, что уже не интересуешься тем, что раньше радовало?\n\n"
                          "Сумма ≥ 12 — стоит отнестись к себе внимательнее. Это не диагноз, "
                          "а сигнал: тебе нужен отдых и, возможно, разговор со специалистом.")
        elif text == "дневник":
            send(user_id, "Как энергия сейчас — от 1 до 10? И одним словом: "
                          "что вымотало больше всего?")
        elif text == "поговорить":
            send(user_id, "Я рядом и слушаю. Расскажи, что происходит, — своими словами.")
        else:
            send(user_id, f"Я понимаю тебя. {MENU}")
