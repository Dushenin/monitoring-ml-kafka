import hydra
from nodes.SendInfoPersonDBNode import SendInfoPersonDBNode
from nodes.DetectionNode import DetectionNode
from nodes.KafkaProducerNode import KafkaProducerNode
from kafka import KafkaConsumer
from json import loads


@hydra.main(version_base=None, config_path="configs", config_name="app_config")
def main(config) -> None:
    
    detection_node = DetectionNode(config)
    send_info_db_node = SendInfoPersonDBNode(config)
    send_kafka_node = KafkaProducerNode(config)

    topic = bootstrap_servers = config["kafka_consumer"]["topic_name"]
    bootstrap_servers = config["kafka_consumer"]["bootstrap_servers"]

    kafka_consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda x: loads(x.decode("utf-8")),
    )

    for message in kafka_consumer:
        data = message.value
        predict = detection_node.process(data)

        send_info_db_node.insert_data(predict, data['taskId'], data['url'], data['timestamp_find_image'])
        send_kafka_node.process(predict, data['taskId'], data['url'], data["bucket_s3"])
  


if __name__ == "__main__":
    main()
