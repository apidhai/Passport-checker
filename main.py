import os
import time
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TARGET_URL = "https://krakow.pasport.org.ua/solutions/e-queue"
CHECK_INTERVAL = 180  # проверка каждые 3 минуты


def send_telegram_message(message: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[!] Ошибка: Не заданы TELEGRAM_TOKEN или CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[!] Ошибка отправки в Telegram: {e}")


def check_queue():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Проверка наличия мест...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text()

            # Фразы, определяющие отсутствие слотов
            no_slots_keywords = [
                "Немає вільних місць",
                "Вільні дні відсутні",
                "Запис відсутній",
                "немає вільних слотів"
            ]

            has_no_slots = any(keyword.lower() in text_content.lower() for keyword in no_slots_keywords)

            if not has_no_slots:
                msg = (
                    "🚨 <b>ВНИМАНИЕ! Похоже, появились свободные места в Кракове!</b>\n\n"
                    f"Ссылка для записи: {TARGET_URL}"
                )
                print("[+] НАЙДЕНЫ МЕСТА! Отправляем сообщение...")
                send_telegram_message(msg)
            else:
                print("[-] Мест пока нет.")
        else:
            print(f"[!] Ошибка доступа к сайту, код ответа: {response.status_code}")

    except Exception as e:
        print(f"[!] Ошибка во время запроса: {e}")


def main():
    send_telegram_message("☁️ Скрипт проверки очереди в Кракове запущен в облаке (Render)!")
    while True:
        try:
            check_queue()
        except Exception as e:
            print(f"[!] Ошибка: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
