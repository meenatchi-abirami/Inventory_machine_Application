import logging
import os
from functools import wraps
from typing import Optional, Dict
from graypy import GELFUDPHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def gathering_graylogger_info():
    server_info = {
        "graylog_host" : os.getenv('GRAYLOG_HOST', 'localhost'),
        "graylog_port" : int(os.getenv('GRAYLOG_PORT', 12201)),
        "app_name" : os.getenv('APP_NAME', 'common_route'),
        "environment" : os.getenv('ENVIRONMENT', 'dev')
    }
    return server_info

class BaseLoggerConfig:
    def __init__(self, log_level: str, server_info: Dict, formatter: logging.Formatter) -> None:
        self.log_level = log_level
        self.formatter = formatter
        self.server_info = server_info

    def configure_graylog_handler(self) -> GELFUDPHandler:
        graylog_handler = GELFUDPHandler(self.server_info.get('graylog_host'), self.server_info.get('graylog_port'), 
                                        extra_fields = {"app_name": self.server_info.get('app_name'), "environment": self.server_info.get('environment')})
        graylog_handler.setFormatter(self.formatter)
        return graylog_handler

class LoggerManager:
    _loggers = {}

    @classmethod
    def get_logger(cls, name: str, config: BaseLoggerConfig) -> logging.Logger:
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(config.log_level)
            logger.addHandler(config.configure_graylog_handler())
            cls._loggers[name] = logger
        return cls._loggers[name]

# Specific configurations for different logging needs
class LoggingComponent:

    def __init__(self) -> None:
        self.formatter = logging.Formatter('%(asctime)s - %(host)s - %(user)s - %(source)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
        # Configurations for different loggers
        self.log_server_info = gathering_graylogger_info()
        self.gray_logs = BaseLoggerConfig(logging.DEBUG, self.log_server_info, self.formatter)

    def get_gray_logger(self) -> logging.Logger:
        return LoggerManager.get_logger('Ausweg-XLogger-Ems', self.gray_logs)

logging_component = LoggingComponent()