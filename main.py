import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import re
import threading
import sqlite3
import config
import database as db

db.init_db()

def start_user_bot(user_token, user_id):
    try:
        user_session = vk_api.VkApi(token=user_token)
        u_vk = user_session.get_api()
        user_longpoll = VkLongPoll(user_session)
        me = u_vk.users.get()
        print(f"🛰️ Юзербот [{me[0]['first_name']} {me[0]['last_name']}] успешно запущен в чатах!")
        for event in user_longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.from_chat and not event.from_me:
                peer_id, sender_id, text, msg_id = event.peer_id, event.user_id, event.text, event.message_id
                text_lower = text.lower()
                for rule_id, rule_info in config.RULES.items():
                    triggered = False
                    for trigger in rule_info["triggers"]:
                        if re.search(r"\b" + re.escape(trigger) + r"\b", text_lower):
                            triggered, matched_word = True, trigger
                            break
                    if triggered:
                        iris_cmd, punishment, rule_name, rule_emoji = rule_info["iris_cmd"], rule_info["punishment"], rule_info["name"], rule_info["emoji"]
                        if punishment == "предупреждение":
                            current_warns = db.add_user_warn(sender_id)
                            if current_warns >= 3:
                                iris_cmd, punishment = "!мут 1 д", "Мут 24 часа (Превышен лимит 3/3 ⚠️)"
                                db.reset_user_warns(sender_id)
                            else:
                                punishment = f"Предупреждение ({current_warns}/3 ⚠️)"
                        u_vk.messages.send(peer_id=peer_id, message=iris_cmd, reply_to=msg_id, random_id=0)
                        log_chat_id = db.get_log_chat() or config.LOG_PEER_ID
                        user_role = db.get_user_role(sender_id) or "Игрок 🛡️"
                        current_chat_name = db.get_chat_name(peer_id)
                        log_message = (
                            f"🚨 [АВТО-НАКАЗАНИЕ ОТ ЮЗЕРБОТА]\n━━━━━━━━━━━━━━━━━━━━━\n"
                            f"👤 *Нарушитель:* [id{sender_id}|Пользователь]\n"
                            f"💼 *Должность:* {user_role}\n"
                            f"💬 *Чат / Направление:* {current_chat_name}\n"
                            f"📋 *Причина:* Пункт {rule_id} ({rule_name})\n"
                            f"⚡ *Выдано:* {punishment.upper()}\n━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📌 *{rule_emoji} {rule_name} // {current_chat_name}*\n\n"
                            f"👇 Ниже переслано нарушение:"
                        )
                        u_vk.messages.send(peer_id=log_chat_id, message=log_message, forward_messages=msg_id, random_id=0)
                        break
    except Exception as e:
        print(f"❌ Ошибка в потоке юзербота {user_id}: {e}")

try:
    group_session = vk_api.VkApi(token=config.TOKEN)
    vk = group_session.get_api()
    group_id = 240438318 
    longpoll = VkBotLongPoll(group_session, group_id)
    print(f"✅ Главная панель группы успешно запущена для ID: {group_id}")
except Exception as e:
    print(f"❌ Ошибка авторизации группы: {e}")
    exit()

def send_group_msg(peer_id, text, keyboard=None):
    params = {"peer_id": peer_id, "message": text, "random_id": 0}
    if keyboard: params["keyboard"] = keyboard
    vk.messages.send(**params)

def get_main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🚀 Подключить бота", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("❓ Инструкция", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("📋 Список команд", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

try:
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS user_tokens (user_id INTEGER PRIMARY KEY, token TEXT)")
    cursor.execute("SELECT user_id, token FROM user_tokens")
    saved_bots = cursor.fetchall()
    conn.close()
    for b_id, b_token in saved_bots:
        threading.Thread(target=start_user_bot, args=(b_token, b_id), daemon=True).start()
except Exception as e:
    print(f"Не удалось автозапустить старых ботов: {e}")

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.obj.message
        peer_id, user_id, text = msg['peer_id'], msg['from_id'], msg['text']
        text_lower = text.lower()
        if user_id < 0 or peer_id > 2000000000: continue
        if text_lower in ["привет", "начать", "start", "меню"]:
            send_group_msg(peer_id, "👋 Привет! Я управляющая система MD-tools. Воспользуйся кнопками ниже для настройки модерации.", keyboard=get_main_keyboard())
            continue
        elif text == "🚀 Подключить бота":
            send_group_msg(peer_id, "🔑 Отправьте вашу ссылку с токеном Kate Mobile для привязки вашего страничного бота к нашей системе.")
            continue
        elif text == "❓ Инструкция":
            send_group_msg(peer_id, "🛠️ Инструкция:\n1. Нажмите «🚀 Подключить бота».\n2. Перейдите по ссылке, выберите Kate Mobile.\n3. Скопируйте ссылку из адресной строки и отправьте её сюда.")
            continue
        elif text == "📋 Список команд":
            roles_str = "\n".join([f"• {r}" for r in config.ROLES])
            send_group_msg(peer_id, config.HELP_TEXT.format(p=config.PREFIX, roles=roles_str))
            continue
        elif "vk1.a." in text:
            token = text
            match = re.search(r"access_token=(vk1\.a\.[A-Za-z0-9_-]+)", text)
            if match: token = match.group(1)
            db.save_user_token(user_id, token)
            send_group_msg(peer_id, "✅ **Токен получен!** Страничный бот успешно привязан и прямо сейчас запускается в фоне для модерации ваших 5 чатов.")
            threading.Thread(target=start_user_bot, args=(token, user_id), daemon=True).start()
            continue

