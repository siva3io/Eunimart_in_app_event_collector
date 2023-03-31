__author__ = 'Pavan Kumar(pavan@eunimart.com)'
__version__ = '0.0.1'

LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(message)s"
            },
            "extended": {
                'format': '[{asctime}] : [{levelname}] : [PATH: {name}.{module}.{funcName}] : [lineno: {lineno}] : {message}',
                'style': '{',
            },
            "json": {
                "format": "time: {asctime}, level: {levelname}, name: {name}.{module}.{funcName} lineno: {lineno}, message: {message}",
                'style': '{'
                }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
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
            'consumer':{
                "level": "DEBUG",
                "handlers": ["console"],
                'propagate': False
            },
            'publisher':{
                "level": "DEBUG",
                "handlers": ["console"],
                'propagate': False
            }
        }
    }


import logging.config
    
logging.config.dictConfig(LOGGING_CONFIG)