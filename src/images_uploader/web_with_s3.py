import logging
import os
from kafka import KafkaProducer
from local_utils.S3Uploader import S3Uploader
from json import dumps
from faker import Faker
import time
import streamlit as st
import numpy as np
import cv2


class SendResults:
    """Модуль отпраки сообщения в кафку и сохранения фотки в S3:"""

    def __init__(self) -> None:
        self.kafka_bootstrap_servers: str = "127.0.0.1:9092"
        self.kafka_topic: str = "imageForChecking"
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=self.kafka_bootstrap_servers,
            value_serializer=lambda x: dumps(x).encode("utf-8"),
        )
        self.s3_bucket_name = "input-images"
        self.s3_uploader = S3Uploader(self.s3_bucket_name)
        self.fake = Faker()

    def process(self, img, path):
        data = {
            "taskId": str(self.fake.uuid4()),
            "url": path,
            "bucket_s3": self.s3_bucket_name,
            "timestamp_find_image": time.time(),
        }
        self.s3_uploader.upload_cv2_frame(img, path)
        self.kafka_producer.send(self.kafka_topic, value=data).get(timeout=1)


results_sender = SendResults()
st.title("Загрузка фотографий")
uploaded_files = st.file_uploader("Загрузите фотографии", type=["jpg", "jpeg", "png"], accept_multiple_files=True)


def process_image(uploaded_file, image_path):
    try:
        img = np.array(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)  # bgr view
        #gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        results_sender.process(img, image_path)
        return True
    except Exception as e:
        st.error(f"Ошибка при обработке фотографии: {e}")
        return False

if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        image_path = uploaded_file.name
        # Получение имени файла без расширения
        file_name, file_extension = os.path.splitext(image_path)
        # Изменение расширения на '.jpeg'
        s3_image_path = f"{file_name}.jpeg"
        if process_image(uploaded_file, s3_image_path):
            st.success(f"Фотография {uploaded_file.name} успешно загружена")
        else:
            st.error(f"Ошибка при обработке фотографии {uploaded_file.name}")
