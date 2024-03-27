from kafka import KafkaConsumer
import telebot
from json import loads
from telebot import types
import time
import threading
import yaml
from minio import Minio
import numpy as np
import cv2
import os

from nodes.SentInfoPersonDBNode import SentInfoPersonDBNode


# Открываем YAML файл
with open('configs/app_config.yaml', 'r') as file:
    # Загружаем содержимое файла
    config = yaml.safe_load(file)

# глобальные переменные:
TOKEN = config["telegram_token"]
CHAT_ID = config["chat_id"]
url = None
predict = None
task_id = None
flag = False  # Flag to control the waiting mechanism of kafka пока не дан ответ юзера
sent_info_db_node = SentInfoPersonDBNode(config)

# S3 configuration 
minio_client = Minio(
    config["s3"]["server_address"],
    access_key=config["s3"]["s3_access_key"],
    secret_key=config["s3"]["s3_secret_key"],
    secure=False,
)

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)


# Функция отправки сообщения в чат при приходе новой фотки
def send_message(msg_value):
    global url, predict, task_id
    url = msg_value['url']
    predict = msg_value['predict']
    task_id = msg_value["task_id"]
    bucket_name = msg_value['bucket_s3']
    # Определяем текст сообщения в зависимости от предсказания
    if predict:
        prediction_text = "Нейронная сеть считает что на фото ЕСТЬ человек"
    else:
        prediction_text = "Нейронная сеть считает что на фото НЕТ человека"


    # Получаем объект изображения из s3
    try:
        response = minio_client.get_object(bucket_name, url)
        image_data = response.read()
        # Читаем изображение в формате OpenCV из полученных данных
        img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        # сохраняем фотку пришедшую из s3 под именем 'infer_img.jpg'
        cv2.imwrite('infer_img.jpg', img)
    except:
        print(f"Downloading the image from S3 failed | {url}")


    markup = types.InlineKeyboardMarkup()
    button_ignore = types.InlineKeyboardButton(text="Игнорировать", callback_data="ignore")
    markup.row(button_ignore)
    button_yes = types.InlineKeyboardButton(text="Человек", callback_data="human")
    button_no = types.InlineKeyboardButton(text="Не Человек", callback_data="no_human")
    markup.row(button_yes, button_no)

    # Отправляем сообщение с текстом предсказания и изображением, а также клавиатурой с кнопками
    bot.send_message(chat_id=CHAT_ID, text='------------------')
    bot.send_message(chat_id=CHAT_ID, text=prediction_text)
    # отображаем 'infer_img.jpg'
    bot.send_photo(chat_id=CHAT_ID, photo=open('infer_img.jpg', 'rb'), reply_markup=markup)

    if os.path.exists('infer_img.jpg'):
        # Удаляем файл
        os.remove('infer_img.jpg')


# Обработчик выбора ответа на вопрос что на фотке
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global flag
    # Remove the inline keyboard markup after a button is pressed
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    data = {}
    data['taskId'] = task_id
    data['timestamp'] = time.time()

    if call.data == "human":
        flag = True
        bot.send_message(chat_id=CHAT_ID, text=f'Итоговый выбор: Человек на фото')
        data['checkHuman'] = True
        sent_info_db_node.insert_data(data)

    elif call.data == "no_human":
        flag = True
        bot.send_message(chat_id=CHAT_ID, text=f'Итоговый выбор: Нет человека на фото')
        data['checkHuman'] = False
        sent_info_db_node.insert_data(data)

    elif call.data == "ignore":
        flag = True
        bot.send_message(chat_id=CHAT_ID, text=f'Игнорируем эту фотографию')
    

# обработчик команды /get_chat_info чтобы узнать id чата для указания в конфиге
@bot.message_handler(commands=['get_chat_info'])
def get_chat_info(message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    bot.reply_to(message, f"Имя чата: {chat_title}, id {chat_id}")


def kafka_consumer():
    global flag
    flag = True
    consumer = KafkaConsumer(
        config["kafka_comsumer"]["topic"],
        bootstrap_servers=config["kafka_comsumer"]["bootstrap_servers"],
        value_deserializer=lambda x: loads(x.decode("utf-8")),
    )

    for message in consumer:
        msg_value = message.value
        send_message(msg_value)
        flag = False
        while not flag:
            pass
        time.sleep(3) # ожидаем 3 секунды новое сообщение

def bot_polling():
    try:
        #bot.infinity_polling()
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"Ошибка в потоке Telegram бота: {e}")

# 2 потока сделал чтобы обрабатывать паралльельно бесконечный цикл кафки и тг бота
kafka_thread = threading.Thread(target=kafka_consumer)
bot_thread = threading.Thread(target=bot_polling)

kafka_thread.start()
bot_thread.start()

kafka_thread.join()
bot_thread.join()