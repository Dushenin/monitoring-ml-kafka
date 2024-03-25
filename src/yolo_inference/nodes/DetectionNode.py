from ultralytics import YOLO
import torch
import numpy as np
import cv2


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


    def process(self, path: str) -> int:

        frame = cv2.imread(path)

        results = self.model.predict(frame, imgsz=self.imgsz, conf=self.conf, verbose=False,
                                     iou=self.iou, classes=self.classes_to_detect)
        detected_cls = results[0].boxes.cls.cpu().int().tolist()
        
        return len(detected_cls)>0

    