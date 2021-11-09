import time

import requests

from .auth_token import get_token
from .oauth import authenticate, get_status_cache, update_wait_status
from ..logger import status_logger


# GET content from the given API endpoint while handling common status errors
def get_content(url: str, params=None, headers: str = get_token(), count_limit: int = 3):
    if params is None:
        params = {}

    override_token_header = None

    count = 1
    while count <= count_limit:

        # GET content
        content = requests.get(url=url, params=params,
                               headers=headers if override_token_header is None else override_token_header)
        count += 1

        # GET content status
        status = content.status_code

        # Status based actions
        # Normal
        if status == 200:
            return content

        else:
            # API rate limit reached
            if status == 429:
                wait_time = 60.125
                status_logger.debug(msg="429. Rate Limit: {}".format(url))
                time.sleep(wait_time)

            # Passed a null value
            if status == 400:
                status_logger.debug(msg="400. Invalid params: {}".format(url))
                break

            # Unauthorized / Invalid AuthToken header. Token is likely expired.
            elif status == 401:
                status_logger.debug(msg="401. Invalid token: {}".format(url))

                # Get if another authentication process is running
                if not get_status_cache(wait=False):
                    # Authenticate and get new token header
                    update_wait_status(True)
                    authenticate()
                    update_wait_status(False)
                else:
                    get_status_cache(wait=True)
                override_token_header = get_token()

            # Forbidden / Access Restricted
            elif status == 403:
                status_logger.debug(msg="403. Forbidden or Access Restricted: {}".format(url))
                break

            # Data not found for given Params
            elif status == 404:
                status_logger.debug(msg="404. Data not found for given Params: {}, {}".format(url, params))
                break

            # Server error
            elif status == 500:
                status_logger.Error(msg="500. Server error: {}".format(url))
                break

            # Temporary problem
            elif status == 503:
                status_logger.Error(msg="503. Temporary problem: {}".format(url))
                break
