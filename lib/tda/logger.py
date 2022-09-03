# TD Ameritrade API Logger

import logging
import sys

from defs import TDA_LOG

# Dict of all instantiated loggers
loggers = {}


# TDA Loggers
class TDALogger:
    def __init__(self, logger_name: str, add_streamhandler: bool = True):

        self.logger_name = logger_name

        # If logger exists, return existing logger
        if loggers.get(self.logger_name):
            self.logger = loggers.get(self.logger_name)

        # Otherwise create new logger
        else:
            # Define handlers
            self.file_handler = logging.FileHandler(TDA_LOG, mode='a')

            # Define log formatter
            self.formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

            # Add formatter to handlers
            self.file_handler.setFormatter(self.formatter)

            # Get logger
            self.logger = logging.getLogger(name=self.logger_name)
            self.logger.propagate = False

            # Set Default Level
            self.logger.setLevel(logging.DEBUG)

            # Add handler to logger
            self.logger.addHandler(self.file_handler)

            if add_streamhandler:
                self.stream_handler = logging.StreamHandler(sys.stdout)
                self.stream_handler.setFormatter(self.formatter)
                self.logger.addHandler(self.stream_handler)

            # Save to loggers dict
            loggers[self.logger_name] = self.logger
