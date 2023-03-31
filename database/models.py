from mongoengine import DynamicDocument, IntField, StringField, DateTimeField, DictField, FloatField



class EventLogRoutesRegistry(DynamicDocument):
    
    path = StringField(required=True, unique=True)
    event_log = DictField(required=True)
    event_log_data = DictField(required=True)
    meta = {
        "collection": "event_log_routes_registry",
        }