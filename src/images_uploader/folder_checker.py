from faker import Faker
from kafka import KafkaProducer
from json import dumps
from datetime import datetime, timezone, timedelta
import time
import os


PATH_S3 = "images_for_processing"

topic = "imageForChecking"
bootstrap_servers = "127.0.0.1:9092"


class ImageProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.processed_files = set()

    def get_list_new_images(self):
        new_images = []
        for file in os.listdir(self.folder_path):
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):  # Укажите нужные расширения файлов
                full_path = os.path.join(self.folder_path, file)
                if os.path.isfile(full_path) and full_path not in self.processed_files:
                    new_images.append(full_path)
        return new_images

    def mark_as_processed(self, file_path):
        self.processed_files.add(file_path)

class ImageSender:
    def __init__(self, folder_path, kafka_producer, topic):
        self.image_processor = ImageProcessor(folder_path)
        self.kafka_producer = kafka_producer
        self.topic = topic
        self.fake = Faker()

    def send_images_to_kafka(self):
        current_time = time.time()
        list_files = self.image_processor.get_list_new_images()
        if list_files:
            for full_path in list_files:
                data = {
                    "taskId": str(self.fake.uuid4()),
                    "url": full_path,
                    "timestamp_find_image": current_time
                }
                self.kafka_producer.send(self.topic, value=data)
                print("Sent data:", data)
                self.image_processor.mark_as_processed(full_path)



kafka_producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda x: dumps(x).encode("utf-8"),
)

# Check if the directory exists
if not os.path.exists(PATH_S3):
    # If it doesn't exist, create the directory
    os.makedirs(PATH_S3)
    print(f"Directory '{PATH_S3}' created successfully.")

script_dir = os.getcwd()  # Получаем путь до текущего скрипта
images_dir = os.path.join(script_dir, PATH_S3)  # Папка с изображениями полный путь
image_sender = ImageSender(images_dir, kafka_producer, topic)

while True:
    image_sender.send_images_to_kafka()
    time.sleep(3)