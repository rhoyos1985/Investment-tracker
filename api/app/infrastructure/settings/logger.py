import logging
import sys
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
import os
from typing import Optional

from app.infrastructure.settings.api_settings import settings
from app.util.enums.environment import api_environments

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

class ApiLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.pop('extra', {})
        if extra:
            msg = f"{msg} | {json.dumps(extra, ensure_ascii=False)}"
        return super().process(msg, kwargs)

class JSONFormatter(logging.Formatter):
    
    def format(self, record: logging.LogRecord) -> str:
        msg : str = record.getMessage()
        extra_data: Optional[str] = None

        if "|" in msg:
            msg, extra_data = msg.split("|")
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": msg,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if extra_data:
            log_data["extra_info"] = json.loads(extra_data)
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data, ensure_ascii=False)

class SimpleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if settings.ENVIRONMENT == api_environments.PRODUCTION and not settings.DEBUG:
            msg = msg.split("|")[0]
        new_format = f"[{timestamp}] [{record.levelname}]: {msg}"
        return new_format


def setup_logging():
    logger = logging.getLogger("investment_api")
    logger.setLevel(logging.INFO)
    
    logger.propagate = False
    
    json_formatter = JSONFormatter()
    simple_formatter = SimpleFormatter()
    
    file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "api.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    error_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "error.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)
   
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)

    adapter = ApiLoggerAdapter(logger, {})
    
    return adapter

logger = setup_logging()

