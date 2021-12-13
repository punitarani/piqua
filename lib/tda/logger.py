# TD Ameritrade API Logger

import logging
import sys

from defs import LOG_PATH_tda, LOG_PATH_tda_auth, LOG_PATH_tda_status

log_formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')


# TDA Loggers
class TDALogger:
    def __init__(self, logger_name: str):
        self.logger_name = logger_name

        # Define log formatter
        self.formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

        # Define handlers
        self.file_handler = logging.FileHandler(LOG_PATH_tda, mode='a')
        self.stream_handler = logging.StreamHandler(sys.stdout)

        # Add formatter to handlers
        self.file_handler.setFormatter(self.formatter)
        self.stream_handler.setFormatter(self.formatter)

        # Get logger
        self.logger = self.getLogger()

    # Function to get logger
    def getLogger(self) -> logging.Logger:
        logger = logging.getLogger(name=self.logger_name)
        self.addHandlers(logger)

        # Set Default Level
        logger.setLevel(logging.DEBUG)

        return logger

    # Function to add handlers to logger
    def addHandlers(self, logger: logging.Logger) -> logging.Logger:
        logger.addHandler(self.file_handler)
        logger.addHandler(self.stream_handler)
        return logger
