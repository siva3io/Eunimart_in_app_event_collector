import pika
import umsgpack
import logging
import time

logger = logging.getLogger("publisher")

class Publisher:

    APPLICATION_ID="marketpalce_process_manager"
    DEFAULT_DELIVERY = 2
    CONTENT_TYPE="application/json"

    def __init__(self, amqp_url='amqp://localhost', exchange=''):
        self.amqp_url = amqp_url
        self.exchange = exchange

    def send_message(self, queue, message={}):
        """
        It will serilize the payload and publish that payload to the specific exchange 
        """

        self._publish(routing_key=queue, payload=message)
        

    def _publish(self, routing_key, payload):
        
        serialized_message = umsgpack.packb(payload)
        
        connection = pika.BlockingConnection()
        
        channel = connection.channel()

        properties = pika.BasicProperties(app_id=self.APPLICATION_ID,
                                          content_type=self.CONTENT_TYPE,
                                          delivery_mode=self.DEFAULT_DELIVERY)

        try:
            channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=serialized_message,
                properties=properties
            )

            logger.debug('message was published successfully into %s', routing_key)
            connection.close()


            return True
        except Exception as e:
            logger.error("Error in publish --> %s", e, exc_info=True)
            return False