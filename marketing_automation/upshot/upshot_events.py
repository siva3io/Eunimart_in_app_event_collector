from database.models import EventLogRoutesRegistry
from event_handler.request_handler import RequestHandler
from config import Config, logging_config
import uuid
import requests
import json
from collections import OrderedDict
from ..utils import catch_exceptions

import logging

logger = logging.getLogger("marketing_auto_router")
class Upshot:

    def __init__(self):
        pass

    @catch_exceptions
    def create_payload_upshot(self, msg, event_spec):
    
        outputs = msg
        event_steps = OrderedDict({
            "title":"upshot_integration",
            "description":"upshot_integration",
            "name":"upshot_integration",
            "start_event":"upshot_integration",
            "steps":{         
                "upshot_integration":{            
                    "success":{
                        "event_key":""
                    },
                    "error":{
                        "event_key":"notification.error_message"
                    }
                } 
            }
        })
        event_specs={
            "status":True,
            "event_specs":{
                "config_data" : logging_config,
                "events_steps" : event_steps,
                "event_spec" : event_spec
            }
        }
        event_message = {
            "event_id": uuid.uuid4(),
            "request_id": uuid.uuid4(),
            "event_data":{
                "event_specs":event_specs["event_specs"],
                "outputs":outputs
                }
        }

        request_handler_obj = RequestHandler(config_object=Config)

        request_handler_response = request_handler_obj.proccess_request(event_message)

        return request_handler_response["data"]

    @catch_exceptions
    def send_add_events(self, payload, testing):

        myobj = payload
        if not testing:
            myobj["auth"] ={
                "apiKey": Config.UPSHOT_API_KEY,
                "appId": Config.UPSHOT_APP_ID,
                "accountId": Config.UPSHOT_ACCOUNT_ID
            }
        else:
            myobj["auth"] ={
                "apiKey": Config.UPSHOT_API_KEY_TEST,
                "appId": Config.UPSHOT_APP_ID_TEST,
                "accountId": Config.UPSHOT_ACCOUNT_ID_TEST
            }

        response = requests.post("https://eapi.goupshot.com/v1/events/add",data=json.dumps(myobj))
        
        logger.event_debug("Done with upshot %s",response.content)

        return response.content
        
    @catch_exceptions    
    def upshot_add_event(self, msg, event_spec, testing = False):
        payload = self.create_payload_upshot(msg, event_spec)
        response = self.send_add_events(payload, testing)
        return response
