import os.path
import unittest

from src.loggers import SystemLogger
from defs import ROOT, SYSTEM_LOG


class TestLoggers(unittest.TestCase):
    # Test System Logger Parent
    def test_SystemLogger(self):
        logger = SystemLogger(logger_name="test").logger
        log_msg = "Testing System Logger"

        logger.info(msg=log_msg)

        with open(os.path.join(ROOT, SYSTEM_LOG), 'r') as logs:
            # Skip to last line
            for log in logs:
                continue
            logs.close()

        # Use last log and compare message
        # Last part of log should be "test | INFO | Testing System Logger\n"
        # \n declares end of log msg
        logged_msg = log[-(len(log_msg) + 15):]
        actual_msg = "test | INFO | " + log_msg + "\n"

        self.assertEqual(first=logged_msg, second=actual_msg)

        if logged_msg == actual_msg:
            logger.info(msg="SUCCESS")

    # Test System Logger Child
    def test_SystemLoggerChild(self):
        logger = SystemLogger(logger_name="test.child").logger
        log_msg = "Testing System Logger Child"

        logger.info(msg=log_msg)

        with open(os.path.join(ROOT, SYSTEM_LOG), 'r') as logs:
            # Skip to last line
            for log in logs:
                continue
            logs.close()

        # Use last log and compare message
        # Last part of log should be "test | INFO | Testing System Logger\n"
        # \n declares end of log msg
        logged_msg = log[-(len(log_msg) + 21):]
        actual_msg = "test.child | INFO | " + log_msg + "\n"

        self.assertEqual(first=logged_msg, second=actual_msg)

        if logged_msg == actual_msg:
            logger.info("SUCCESS")


if __name__ == '__main__':
    unittest.main()
