import uuid
import json
import logging
import requests
from datetime import datetime
from collections import OrderedDict
from ..utils import catch_exceptions
from config import  Config, logging_config
from event_handler.request_handler import RequestHandler

logger = logging.getLogger("marketing_auto_router")


ZOHO_ACCESS_TOKEN_URL = 'https://accounts.zoho.com/oauth/v2/token?refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}&grant_type=refresh_token'
ZOHO_APP_MODULE_URL = "https://www.zohoapis.com/crm/v2/{}/upsert"

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ZohoCRM(metaclass = Singleton):

    def __init__(self):
        self.access_token = ""
    
    @catch_exceptions
    def get_outhtoken(self):

        zoho_keys = {
            "client_id": Config.ZOHO_CLIENT_ID,
            "refresh_token": Config.ZOHO_REFRESH_TOKEN
        }
        request_url = ZOHO_ACCESS_TOKEN_URL.format(**zoho_keys)
        access_key_response = requests.post(request_url).json()

        access_key = access_key_response.get('access_token')
        logger.event_debug("Zoho response for upsert %s", access_key )

        if access_key:
            return access_key

        return "NA"

    @catch_exceptions
    def create_payload_for_zoho(self, msg, event_spec):
           
        outputs = msg
        event_steps = OrderedDict({
            "title":"zoho_integration",
            "description":"zoho_integration",
            "name":"zoho_integration",
            "start_event":"zoho_integration",
            "steps":{         
                "zoho_integration":{            
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

        if not isinstance(request_handler_response["data"]["data"],list):
            request_handler_response["data"]["data"] = [request_handler_response["data"]["data"]] 
        
        return request_handler_response["data"]

    @catch_exceptions
    def zoho_upsert(self, module_name, msg, event_spec):
        headers = {
            'Authorization': 'Zoho-oauthtoken {}'.format(self.access_token),
        }
        request_url = "https://www.zohoapis.com/crm/v2/{}/upsert".format(module_name)

        payload = self.create_payload_for_zoho(msg, event_spec)

        if payload['data']!=[{}]:
            print('[]]]]]]]]]]]---',payload)

            response = requests.request("Post", request_url, headers=headers, data = json.dumps(payload))
            
            response = json.loads(response.text.encode('utf8'))
            logger.event_debug("Zoho response for upsert %s", json.dumps(response) )

            if response.get("code","")=="INVALID_TOKEN":
                
                return {
                    "status":False,
                    "code":"INVALID_TOKEN"
                }

            elif response.get('data'):
                
                if response["data"][0].get("code") == "SUCCESS":
                    return {
                        "status": True
                    }
                else:
                    if type(response["data"]) == type([]):
                        
                        return {
                            "status": False,
                            "code": response["data"][0].get("code")
                        }

                    else:
                        
                        return {
                            "status": False,
                            "code": response["data"].get("code")
                        }
        else:
            return {
                "status":False,
                "code":"NOT_INTEGRATED"
            }

    @catch_exceptions    
    def zoho_add_event(self, msg, event_spec, zoho_module = "Users_Data"):
        if self.access_token == "":
            self.access_token = self.get_outhtoken()

        response = self.zoho_upsert(zoho_module, msg, event_spec)
        
        if response.get("code","")=="INVALID_TOKEN":
            self.access_token = self.get_outhtoken()
            response = self.zoho_upsert(zoho_module, msg, event_spec)
        logger.event_debug("Zoho response for upsert %s", json.dumps(response) )
        
        return response

    @catch_exceptions    
    def create_segment_payload(self, queue_message):
        query = "(Name:equals:{})"
        segment_record_id = self.get_record_id('Segment_Names',"(Name:equals:{})".format(queue_message["segment_name"]))[0]
        user_record_ids = []
        for i in range(0,len(queue_message["registered_users"]),10):
            new_query = ""
            for j in range(i,i+10):
                if j < len(queue_message["registered_users"]):
                    new_query =new_query+' or '+query.format(queue_message["registered_users"][j])
            user_record_ids.extend(self.get_record_id('Users_Data',new_query))
        
        data = []
        for each_id in user_record_ids:
            data.append({"Account_ID":each_id,"Segments":segment_record_id})
        return data

    @catch_exceptions
    def batch_upsert(self, data, module_name):
        request_url = ZOHO_APP_MODULE_URL.format(module_name)
        headers = {
            'Authorization': 'Zoho-oauthtoken {}'.format(self.access_token),
        }
        for index in range(0, len(data),100):
            payload = {
                "data":[]
            }

            logger.event_debug("sent %s to %s indices %s ", index, index+100, json.dumps(payload))


    @catch_exceptions    
    def get_record_id(self, module_name, query):
        request_url = "https://www.zohoapis.com/crm/v2/{0}/search?criteria=({1})".format(module_name,query)
        headers = {
            'Authorization': 'Zoho-oauthtoken {}'.format(self.access_token),
        }
        response = requests.request("GET", request_url, headers=headers)
        response = response.text.encode('utf8')
        response = json.loads(response)
        if response.get("code","")=="AUTHENTICATION_FAILURE":
            self.access_token = self.get_outhtoken()
            return self.get_record_id(module_name,query)
        ids = []
        for each_record in response.get("data",[]):
            ids.append(each_record["id"])
        return ids





