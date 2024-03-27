import io
import numpy as np
import cv2
from PIL import Image
from minio import Minio
import logging
from json import dumps

# Создание обработчика, который будет выводить логи на консоль
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # стутус INFO задаим (тут его как раз можно менять)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Устанавливаем уровень логирования для обработчика на INFO
# Создание форматировщика
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# Добавление обработчика к регистратору
logger.addHandler(console_handler)


class S3Uploader:
    def __init__(self, bucket_name) -> None:
        self.bucket_name = bucket_name
        self.server_address = "127.0.0.1:9006"
        self.s3_access_key = "s3_access_key"
        self.s3_secret_key = "s3_secret_key"
        self.client = Minio(
            self.server_address,
            access_key=self.s3_access_key,
            secret_key=self.s3_secret_key,
            secure=False,
        )

        # самый быстрый для сериализации формат - jpeg
        self.img_extention = "jpeg"

    def upload_cv2_frame(self, frame: np.ndarray, save_path: str):
        bucket_name = self.bucket_name
        assert (
            save_path[-len(self.img_extention) :] == self.img_extention
        ), f"only .{self.img_extention} images is available, but save_path: {save_path}"
        byteframe = self._frame_to_byte_stream(frame)
        logger.info(f"uploading frame to S3 | {self.server_address}")

        if not self.client.bucket_exists(bucket_name):
            logger.info(f"creating bucket {bucket_name}")
            self.client.make_bucket(bucket_name)

        self.client.put_object(
            bucket_name,
            save_path,
            byteframe,
            byteframe.getbuffer().nbytes,
            content_type="application/octet-stream",
        )
        return save_path

    def _frame_to_byte_stream(self, frame: np.ndarray) -> io.BytesIO:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame_in_bytes = io.BytesIO()
        frame.save(frame_in_bytes, format=self.img_extention.upper())
        # reset file pointer to start
        frame_in_bytes.seek(0)
        return frame_in_bytes
