import os
import time
import random
import asyncio
import pyrogram
import logging
import schedule

from datetime import datetime, timedelta
from dotenv import load_dotenv
from pyrogram import Client, errors, filters, idle
from pyrogram.handlers import MessageHandler

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("bot.log"),
                              logging.StreamHandler()])


load_dotenv(override=True)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
CHAT_USERNAME = os.getenv("CHAT_USERNAME")
SELF_USERNAME = os.getenv("SELF_USERNAME")
logging.info('Environment variables loaded.')


app = Client("my_account", api_id=API_ID, api_hash=API_HASH)
logging.info('Client created.')


"""
TODO:
отложить сообщение
выбрать время
отменить сообщение на утро / вечер
отменить сообщение на завтра
поменять базу/комплимент/эмодзи
"""

def random_time(start_time_str, end_time_str):
    start_time = datetime.strptime(start_time_str, "%H:%M")
    end_time = datetime.strptime(end_time_str, "%H:%M")
    if end_time < start_time:
        end_time += timedelta(days=1)
    delta_seconds = int((end_time - start_time).total_seconds())
    random_seconds = random.randint(0, delta_seconds)
    random_time = start_time + timedelta(seconds=random_seconds)
    return random_time.strftime("%H:%M")


def random_night_message():
    base_msg = {
        '1': 'cладких споть',
        '2': 'cладких снов',
        '3': 'уютных споть',
        '4': 'до завтра',
        '5': 'спокойной ночи',
        '6': 'споки ноки'
    }
    compliment = {
        '1': ', моя кегелька',
        '2': ', кегелька',
        '3': ', зайка', 
        '4': ', шушуля',
        '5': ''
    }
    emoji = {
        '1': ' ❤️',
        '2': ' 💓',
        '3': ' 💞',
        '4': ' 💤',
        '5': ' 🥰✨',
        '6': ' 🥰',
        '7': ' ❤️❤️❤️',
        '8': ' ✨',
        '9': ' 🥰🥰🥰',
        '10': ''
    }
    return random.choice(list(base_msg.values()))+random.choice(list(compliment.values()))+random.choice(list(emoji.values()))


async def send_message(msg: str) -> None:
    try:
        await app.send_message(CHAT_USERNAME, msg)
        logging.info(f"Сообщение отправлено: {datetime.now()}")
    except errors.RPCError as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")
        try:
            await app.send_message(SELF_USERNAME, f"Ошибка при отправке сообщения: {e}")
            logging.info(f"Сообщение об ошибке отправлено себе: {datetime.now()}")
        except errors.RPCError as error:
            logging.error(f"Не удалось отправить сообщение об ошибке себе: {error}")


async def night() -> None:
    night_msg = random_night_message()
    night_time = random_time("23:44", "01:24")
    await app.send_message(SELF_USERNAME, 
                           f'Сообщение: "{night_msg}" будет отправлено в: {night_time}\n'
                           'Для отмены отправки сообщения ответьте на это сообщение текстом "отмена"\n'
                           'Для изменения времени отправки ответьте на это сообщение текстом "время HH:MM"\n'
                           'Для изменения сообщения ответьте на это сообщение текстом "текст"')
    logging.info(f'Сообщение: "{night_msg}" будет отправлено в: {night_time}')
    schedule.every().day.at('03:21').do(lambda: asyncio.create_task(send_message(night_msg))).tag('night')


# async def handle_response(client, message):
#     logging.info("handle_response triggered")
#     if message.reply_to_message:
#         logging.info("Message is a reply")
#         if message.reply_to_message.from_user.username == SELF_USERNAME:
#             logging.info("Message is a reply to SELF_USERNAME")
#             if message.text.lower() == "отмена":
#                 schedule.clear('night')
#                 await message.reply("Отправка сообщения отменена.")
#                 logging.info("Отправка сообщения отменена.")
#             elif message.text.lower().startswith("время"):
#                 try:
#                     new_time = message.text.split()[1]
#                     schedule.clear('night')
#                     schedule.every().day.at(new_time).do(lambda: asyncio.create_task(send_message(random_night_message()))).tag('night')
#                     await message.reply(f"Время отправки сообщения изменено на: {new_time}.")
#                     logging.info(f"Время отправки сообщения изменено на: {new_time}.")
#                 except IndexError:
#                     await message.reply("Пожалуйста, укажите время в формате HH:MM.")
#             elif message.text.lower().startswith("текст"):
#                 new_message = " ".join(message.text.split()[1:])
#                 schedule.clear('night')
#                 schedule.every().day.at(random_time("23:44", "01:24")).do(lambda: asyncio.create_task(send_message(new_message))).tag('night')
#                 await message.reply(f"Сообщение изменено на: {new_message}.")
#                 logging.info(f"Сообщение изменено на: {new_message}.")  
    

async def main():
    await app.start()
    # app.add_handler(MessageHandler(handle_response))
    # logging.info("Handler added.")
    schedule.every().day.at('21:00').do(lambda: asyncio.create_task(night()))
    schedule.every().day.at('05:00').do(lambda: schedule.clear('night'))
    logging.info("Скрипт запущен. Ожидание заданий...")
    
    # await pyrogram.idle()

    try:
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Скрипт остановлен пользователем.")
    except Exception as e:
        logging.error(f"Ошибка в основном цикле: {e}")
    finally:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
