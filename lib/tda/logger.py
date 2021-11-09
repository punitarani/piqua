# TD Ameritrade API Logger

import logging
from pathlib import Path

# tda_auth log
auth_log_path = Path.joinpath(Path(__file__).parent.parent.parent, Path('logs/tda_auth.log'))
auth_logger = logging.getLogger(name='tda_api_auth')
auth_logger.setLevel(logging.DEBUG)
auth_log_handler = logging.FileHandler(auth_log_path.__str__(), mode='a')
auth_log_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
auth_logger.addHandler(auth_log_handler)
auth_logger.addHandler(logging.StreamHandler())


# tda_status log
status_log_path = Path.joinpath(Path(__file__).parent.parent.parent, Path('logs/tda_status.log'))
status_logger = logging.getLogger(name='tda_api_status')
status_logger.setLevel(logging.DEBUG)
status_log_handler = logging.FileHandler(status_log_path.__str__(), mode='a')
status_log_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
status_logger.addHandler(status_log_handler)
status_logger.addHandler(logging.StreamHandler())
