import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import config

try:
    vk_session = vk_api.VkApi(token=config.TOKEN)
    vk = vk_session.get_api()
    # Чистый запуск LongPoll для твоей группы
    longpoll = VkBotLongPoll(vk_session, 240438318)
    print("🚀 ТЕСТ ПРОШЕЛ! Бот группы успешно слушает события!")
    
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            print(f"📩 Пришло новое сообщение: {event.obj.message['text']}")
except Exception as e:
    print(f"❌ Ошибка в тестовом коде: {e}")

