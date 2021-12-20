# Configuring all Loggers

import sys
from defs import SYSTEM_LOG
import logging


# Dict of all instantiated loggers
loggers = {}


# Main System Logger
class SystemLogger:
    def __init__(self, logger_name: str, add_file_handler: bool = True, add_stream_handler: bool = True):
        self.logger_name = logger_name

        # If logger exists, return existing logger
        if loggers.get(self.logger_name):
            self.logger = loggers.get(self.logger_name)

        # Otherwise create new logger
        else:
            # input params
            self.add_file_handler = add_file_handler
            self.add_stream_handler = add_stream_handler

            # Define log formatter
            self.formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

            # Define handlers
            self.file_handler = logging.FileHandler(SYSTEM_LOG, mode='a')
            self.file_handler.setFormatter(self.formatter)
            self.stream_handler = logging.StreamHandler(sys.stdout)
            self.stream_handler.setFormatter(self.formatter)

            # Get logger
            self.logger = self.getLogger()

            # Set default logging level to DEBUG
            self.logger.setLevel(logging.DEBUG)

            # Save to loggers dict
            loggers[self.logger_name] = self.logger

    # Function to get logger
    def getLogger(self) -> logging.Logger:
        logger = logging.getLogger(name=self.logger_name)
        self.addHandlers(logger)
        return logger

    # Function to add handlers to logger
    def addHandlers(self, logger: logging.Logger) -> logging.Logger:

        # Add handler iff logger is parent (i.e. not child) and requested
        if ("." not in self.logger_name) and self.add_file_handler:
            logger.addHandler(self.file_handler)

        if ("." not in self.logger_name) and self.add_stream_handler:
            logger.addHandler(self.stream_handler)

        return logger
