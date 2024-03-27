from ultralytics import YOLO
import torch
import numpy as np
import cv2
from minio import Minio
import logging

logger = logging.getLogger(__name__)


class DetectionNode:
    """Модуль инференса модели детекции"""

    def __init__(self, config) -> None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f'Детекция будет производиться на {device}')

        config_yolo = config["detection_node"]
        self.model = YOLO(config_yolo["weight_pth"])
        self.model.fuse()
        self.classes = self.model.names
        self.conf = config_yolo["confidence"]
        self.iou = config_yolo["iou"]
        self.imgsz = config_yolo["imgsz"]
        self.classes_to_detect = config_yolo["classes_to_detect"]

        # S3 configuration 
        server_address = "127.0.0.1:9006"
        s3_access_key = "s3_access_key"
        s3_secret_key = "s3_secret_key"
        self.minio_client = Minio(
            server_address,
            access_key=s3_access_key,
            secret_key=s3_secret_key,
            secure=False,
        )


    def process(self, kafka_message: dict) -> int:

        # Имя бакета и путь к изображению внутри бакета
        bucket_name = kafka_message['bucket_s3']
        image_key = kafka_message['url']

        # Получаем объект изображения из s3
        try:
            response = self.minio_client.get_object(bucket_name, image_key)
            image_data = response.read()
            # Читаем изображение в формате OpenCV из полученных данных
            frame = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            logger.info(f"The image from S3 is downloaded")
        except:
            logger.warning(f"Downloading the image from S3 failed | {image_key}")

        results = self.model.predict(frame, imgsz=self.imgsz, conf=self.conf, verbose=False,
                                     iou=self.iou, classes=self.classes_to_detect)
        detected_cls = results[0].boxes.cls.cpu().int().tolist()
        
        return len(detected_cls)>0

    