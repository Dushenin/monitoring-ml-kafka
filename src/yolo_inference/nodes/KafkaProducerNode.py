from kafka import KafkaProducer
from json import dumps

import logging


class KafkaProducerNode:
    def __init__(self, config) -> None:
        config_kafka = config["kafka_producer_node"]
        bootstrap_servers = config_kafka["bootstrap_servers"]
        self.topic_name = config_kafka["topic_name"]

        self.kafka_producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: dumps(x).encode("utf-8"),
        )

    def process(self, predict: bool, task_id, url, bucket_s3) -> None:

        data = {
            "task_id": task_id,
            "predict": predict,
            "url": url,
            "bucket_s3": bucket_s3,
        }
        self.kafka_producer.send(self.topic_name, value=data).get(timeout=1)
        logging.info(f"KAFKA sent message: {data} topic {self.topic_name}")
