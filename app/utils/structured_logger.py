import logging
import sys
import os
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

def setup_logging(app):
    log_level = app.config.get('LOG_LEVEL', 'INFO').upper()
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    
    # Remove default handlers
    for h in app.logger.handlers[:]:
        app.logger.removeHandler(h)
        
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    
    # Also configure Werkzeug and other loggers
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    return app.logger
