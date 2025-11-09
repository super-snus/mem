import socket
import time
import requests
import telebot

BOT_TOKEN = "8248310335:AAECHoL6wOvpNxJ2DDsdmGHRTeNjOQybU3s"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

def get_public_ip(timeout=5):
    try:
        resp = requests.get("https://api.ipify.org?format=text", timeout=timeout)
        resp.raise_for_status()
        return resp.text.strip()
    except Exception as e:
        return f"Ошибка получения внешнего IP: {e}"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Ошибка получения локального IP: {e}"

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    public_ip = get_public_ip()
    local_ip = get_local_ip()
    text = (
        "IP отчёт:\n"
        f"Внешний (public) IP: {public_ip}\n"
        f"Локальный (local) IP: {local_ip}"
    )
    try:
        bot.send_message(chat_id, text)
    except Exception as e:
        # пробуем ещё раз при ошибке
        try:
            time.sleep(1)
            bot.send_message(chat_id, f"Ошибка при отправке сообщения: {e}")
        except Exception:
            pass

def main():
    # Надёжный цикл polling с авто-reconnect
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print("Polling упал, повторный запуск через 5 сек. Ошибка:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
