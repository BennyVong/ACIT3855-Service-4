import datetime

import connexion
from connexion import NoContent
from flask_cors import CORS, cross_origin
from pykafka import KafkaClient
import logging.config
import json
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def get_nth_inventory(position):
    logger.info("Get nth Inventory")
    client = KafkaClient(hosts="{}:{}".format(app_config["kafka"]["domain"], app_config["kafka"]["port"]))
    topic = client.topics[app_config["kafka"]["topic"]]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)
    offset = 0
    for message in consumer:
        print(message)
        if message is not None and json.loads(message.value)['type'] == 'inventory':
            if offset == position:
                return json.loads(message.value)['payload'], 200

            offset += 1

    return NoContent, 404


def get_nth_status(start_date, end_date):
    logger.info("Get nth Status")
    client = KafkaClient(hosts="{}:{}".format(app_config["kafka"]["domain"], app_config["kafka"]["port"]))
    topic = client.topics[app_config["kafka"]["topic"]]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)
    for message in consumer:
        if message is not None and json.loads(message.value)['type'] == 'status' and start_date <= json.loads(message.value)['datetime'] <= end_date:
            return json.loads(message.value)['payload'], 200

    return NoContent, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml")

CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    app.run(port=8101)
