from os import getenv, path
from dotenv import load_dotenv

APP_ROOT = path.join(path.dirname(__file__), '.')   # refers to application_top
dotenv_path = path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)



logging_config = {
    "dev":{
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(message)s"
            },
            "extended": {
                'format': '[{asctime}] : [{levelname}] : [request_id:{request_id}] : [event_id:{event_id}] : [PATH: {name}.{module}.{funcName}] : [lineno: {lineno}] : {message}',
                'style': '{',
            },
            "json": {
                "format": "time: {asctime}, level: {levelname}, name: {name}.{module}.{funcName} lineno: {lineno}, request_id:{request_id}, event_id:{event_id}, message: {message}",
                'style': '{'
                }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "EVENT_DEBUG",
                "formatter": "extended",
                "stream": "ext://sys.stdout"
            },
        },
        'loggers': {
            'gunicorn.error': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'marketing_automation':{
                "level": "EVENT_DEBUG",
                "handlers": ["console"],
                'propagate': False
            }
        }
    },
    "prod":{
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(message)s"
            },
            "extended": {
                'format': '[{asctime}] : [{levelname}] : [request_id:{request_id}] : [event_id:{event_id}] : [PATH: {name}.{module}.{funcName}] : [lineno: {lineno}] : {message}',
                'style': '{',
            },
            "json": {
                "format": "time: {asctime}, level: {levelname}, name: {name}.{module}.{funcName} lineno: {lineno}, request_id:{request_id}, event_id:{event_id}, message: {message}",
                'style': '{'
                }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "extended",
                "stream": "ext://sys.stdout"
            },
            "custom_handler": {
                "level": "EVENT_DEBUG",
                "class": "watchtower.CloudWatchLogHandler",
                "boto3_session": "",
                "log_group": "marketplace_adaptor",
                "stream_name": "EVENT_DEBUG",
                "formatter": "extended"
            },

            "info_file_handler": {
                "level": "INFO",
                "class": "watchtower.CloudWatchLogHandler",
                "boto3_session": "",
                "log_group": "marketplace_adaptor",
                "stream_name": "info",
                "formatter": "extended"
            },
            "debug_file_handler": {
                "level": "DEBUG",
                "class": "watchtower.CloudWatchLogHandler",
                "boto3_session": "",
                "log_group": "marketplace_adaptor",
                "stream_name": "debug",
                "formatter": "extended"
            },
            

            "error_file_handler": {
                "level": "ERROR",
                "class": "watchtower.CloudWatchLogHandler",
                "boto3_session": "",
                "log_group": "marketplace_process_manager",
                "stream_name": "error",
                "formatter": "extended"
            }
            
        },
        'loggers': {
            'gunicorn.error': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            }
        }
    }
}


class Config(object):

    DEPLOY_ENV = getenv('RUN_ENV','dev')

    SERVER_PORT = getenv('SERVER_PORT','9002')

    BOTO3_ACCESS_KEY = getenv('AWS_ACCESS_KEY')
    
    BOTO3_SECRET_KEY = getenv('AWS_SECRET_KEY')

    BOTO3_REGION = getenv('AWS_REGION')
    
    REDIS_HOST = getenv('REDIS_HOST')

    REDIS_PASSWORD = getenv('REDIS_PASSWORD')

    REDIS_PORT = getenv('REDIS_PORT')

    REDIS_DB = getenv('REDIS_DATABASE')

    QUEUE_PROVIDER = getenv('QUEUE_PROVIDER')

    RABBITMQ_URI = getenv('RABBITMQ_URI')
    
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')

    QUEUE_NAME =  getenv('QUEUE_TO_LISTEN')
    
    EVENT_LOG_EXCHANGE_NAME = getenv("EVENT_LOG_EXCHANGE_NAME")

    SYNC_JOBS_EXCHANGE = getenv("EVENT_LOG_EXCHANGE_NAME")
    
    LOGGING_CONFIG = logging_config[getenv('RUN_ENV','dev')]

    EVENT_SPEC_BUCKET = getenv('EVENT_SPEC_S3_BUCKET')

    EVENT_OUTPUT_BUCKET = getenv('EVENT_OUTPUT_S3_BUCKET')

    DYNAMO_DB_TABLE = getenv('DYNAMO_DB_TABLE')

    EVENT_STATE_TABLE = getenv('EVENT_STATE_TABLE')

    JSON_SORT_KEYS=False

    INVOICE_BUCKET = getenv('INVOICE_BUCKET')
    
    UPSHOT_API_KEY = getenv('UPSHOT_API_KEY')

    UPSHOT_APP_ID = getenv('UPSHOT_APP_ID')

    UPSHOT_ACCOUNT_ID = getenv('UPSHOT_ACCOUNT_ID')

    UPSHOT_API_KEY_TEST = getenv('UPSHOT_API_KEY_TEST')

    UPSHOT_APP_ID_TEST = getenv('UPSHOT_APP_ID_TEST')

    UPSHOT_ACCOUNT_ID_TEST = getenv('UPSHOT_ACCOUNT_ID_TEST')

    JWT_TOKEN = getenv('JWT_TOKEN')

    ZOHO_CLIENT_ID = getenv('ZOHO_CLIENT_ID')

    ZOHO_CLIENT_SECRET = getenv('ZOHO_CLIENT_SECRET')

    ZOHO_REFRESH_TOKEN = getenv('ZOHO_REFRESH_TOKEN')
