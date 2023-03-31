import time
import umsgpack
import argparse
import threading
import signal
import logging.config
import os
from boto3.session import Session
import json
from config import Config

from message_queue.publisher import Publisher
from message_queue.consumer import Consumer
# from message_queue.rabbitmq import RabbitMqQueue
from marketing_automation import marketing_auto_router
from mongoengine import *

import base64
import binascii

connect(
    'vdezi_events_management',
    host='mongodb://vdezi_admin_user:2016_vdezi_2020@15.206.80.104:27017/?authSource=admin'
)
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION')



EXCHANGE=Config.EVENT_LOG_EXCHANGE_NAME

DEBUG_LEVELV_NUM = 45

logging.addLevelName(DEBUG_LEVELV_NUM, "IN_APP_DEBUG")


def custom_debug(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_LEVELV_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(DEBUG_LEVELV_NUM, message, args, **kws)
     

logging.Logger.event_debug = custom_debug

boto3_session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)

if Config.DEPLOY_ENV != 'dev':    
    for handler_type in [ "custom_handler", "info_file_handler", "debug_file_handler", "error_file_handler" ]:
        Config.LOGGING_CONFIG["handlers"][handler_type]["boto3_session"] = boto3_session
    
logging.config.dictConfig(Config.LOGGING_CONFIG)

logger = logging.getLogger("marketing_automation")    # loging = logging.LoggerAdapter(logger, extra_info)


def log( message, data="", request_id="", event_id=""):
    
    extra_info = { "request_id":request_id, "event_id":event_id}

    if data:
        logger.event_debug(message, data, extra=extra_info )
    else:
        logger.event_debug(message, extra=extra_info )


log("Logs Setuped")



class QueueHandler:

    EXCHANGE=Config.EVENT_LOG_EXCHANGE_NAME
    SOCKET_TIMEOUT=120
    HEARTBEAT=60

    def __init__(self, routing_key):


        self._consumer = Consumer( 
            amqp_url='{uri}?socket_timeout={socket_timeout}&heartbeat={heartbeat}'.format(uri=Config.RABBITMQ_URI, socket_timeout=self.SOCKET_TIMEOUT, heartbeat=self.HEARTBEAT), 
            exchange=self.EXCHANGE, 
            binding_keys=[routing_key],
            queue=routing_key
        )

        self._publisher = Publisher(amqp_url=Config.RABBITMQ_URI, exchange=self.EXCHANGE)

    def start(self):
        self._consumer.add_consumer_callback(self._callback)
        self._consumer.run()
        
    def _decode_base64(self, body):

        try:
            body = base64.decodestring(body)    
            return body
        except binascii.Error:
            return False

    def _decode_data(self, data, check_flag=False):

        try:
            decode_data = umsgpack.unpackb(data)
            return decode_data
        except Exception as e:
            log(e)
            
            if not check_flag:
                decoded_string = self._decode_base64(data)
                if decoded_string:
                    return self._decode_data(decoded_string, check_flag=True)
                else:
                    return False
            else:
                return False

    def _process_message(self, delivery_tag, body):

        thread_id = threading.get_ident()

        log('Thread id: %s Delivery tag: %s Message body: %s'.format(thread_id, delivery_tag, body))

        event_data = self._decode_data(body)
        
        log("message_from_queue --> %s", event_data)

        if event_data:
            process_complete = marketing_auto_router.router(event_data)
            
            log("send_ack_flag --> %s", process_complete)

            if process_complete:
                self._consumer.add_callback_safe_thread(delivery_tag)
        else:
            #@TODO send this message to dead-letter-exchange
            log("send_ack_flag --> %s", process_complete)

    def _callback(self, ch, method, properties, body):
        print('******** Properties **********',properties )
        delivery_tag = method.delivery_tag
        t = threading.Thread(target=self._process_message, args=(delivery_tag, body))
        t.start()
        




def run_worker(queue_to_listen):
    
    log("Queue Name --> %s", queue_to_listen)

    queue_obj = QueueHandler(routing_key=queue_to_listen)

    queue_obj.start()



def parse_args():
    parser = argparse.ArgumentParser(description = "Event Adaptor")
    parser.add_argument("-queue_name", "--worker_queue",required=True, dest="queue_name", type=str, help="Queue Name to use or listen to")
    args = parser.parse_args()
    return args


def main(arguments):
    params = {
        "queue_name":arguments.queue_name,
    }
    
    run_worker(params["queue_name"])
        

def entry_point():
    args = parse_args()
    main(args)


if __name__=="__main__":

    entry_point()
