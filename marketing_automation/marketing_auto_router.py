import jwt
import json
import logging
import datetime
from .utils import catch_exceptions
from .zoho.zoho_crm import ZohoCRM
from .upshot.upshot_events import Upshot 
from config import Config, logging_config
from database.models import EventLogRoutesRegistry

logger = logging.getLogger("marketing_auto_router")

@catch_exceptions
def get_spec_from_db(url_path):
    event = EventLogRoutesRegistry.objects.filter(path = url_path)
    if event:
        return event[0].event_log_data, event[0].event_log, event[0].zoho_module_name
    else:
        return {}, {}, {}

@catch_exceptions
def decode_jwt_token(token):
    jwt_options = {
        'verify_signature': False,
        'verify_exp': False,
        'verify_nbf': False,
        'verify_iat': False,
        'verify_aud': False
    }
    decoded_jwt = jwt.decode(token,Config.JWT_TOKEN,algorithms=['HS256'],options=jwt_options)    
    return decoded_jwt

@catch_exceptions
def router(queue_message):
    testing = False
    if "type" in queue_message:
        logger.event_debug("queue message --> %s",queue_message )
        if queue_message["type"] == "etl_segment":
            crm = ZohoCRM() 
            logger.event_debug("Done with etl_segment " )

    else:
        if "authorization" in queue_message["request"].get("headers", {}): #for nodejs
            queue_message["request"]["headers"]["jwt"] = decode_jwt_token(queue_message["request"]["headers"]["authorization"].replace("Bearer ",""))
            logger.event_debug("got jwt token ---------------- %s ", json.dumps(queue_message["request"]["headers"]["jwt"]) )
            if queue_message["request"]["headers"]["jwt"] and "vdezi_server" in queue_message["request"]["headers"]["jwt"] and queue_message["request"]["headers"]["jwt"]["vdezi_server"]!="vdeziproduction":
                testing = True

        elif "Authorization" in queue_message["request"].get("headers", {}): #for python 
            queue_message["request"]["headers"]["jwt"] = decode_jwt_token(queue_message["request"]["headers"]["Authorization"].replace("Bearer ",""))
            logger.event_debug("got jwt token ----------------- %s ", json.dumps(queue_message["request"]["headers"]["jwt"]) )
            if queue_message["request"]["headers"]["jwt"] and "vdezi_server" in queue_message["request"]["headers"]["jwt"] and queue_message["request"]["headers"]["jwt"]["vdezi_server"]!="vdeziproduction":
                testing = True


        elif queue_message.get("response",{}).get("data",{}):
            if "token" in queue_message["response"]["data"]:
                queue_message["request"]["headers"]["jwt"] = decode_jwt_token(queue_message["response"]["data"]["token"])

        event_log_data, available_event_log, zoho_module = get_spec_from_db(queue_message["request"]["url"])

        if not event_log_data:
            logger.event_debug("No event log data found")
            return True
            
        current_date = datetime.date.today()
        if "response" in queue_message:
            queue_message["response"]["current_date_and_time"]= current_date.isoformat()
        if "response" in queue_message and queue_message["response"].get("status",""):
            queue_message["response"]["status"]=str(queue_message["response"]["status"]) 
        if "error" in queue_message and "status" in queue_message["error"]:
            queue_message["error"]["status"]=str(queue_message["error"]["status"]) 

        if  available_event_log and available_event_log["in_upshot"]:
            upshot = Upshot()
            response_upshot = upshot.upshot_add_event(queue_message, event_log_data["upshot"],testing = testing)
            logger.event_debug("Done with upshot" )

        if available_event_log and available_event_log["in_zoho"]:
            crm = ZohoCRM() 
            response_zoho = crm.zoho_add_event(queue_message, event_log_data.get("zoho",{}), zoho_module)
            logger.event_debug("disabled zoho")

    return True
