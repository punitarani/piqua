import pickle
import time
from datetime import datetime

import requests

from .oauth import TOKEN_PATH, authenticate


# Get token header
def get_token(test: bool = False):
    # Test if token has expired
    def test_token(t):
        endpoint = r'https://api.tdameritrade.com/v1/userprincipals'
        content = requests.get(url=endpoint, headers=t)

        if content.status_code == 429:
            time.sleep(61 - datetime.now().second)
            content = requests.get(url=endpoint, headers=t)

        # User Principals JSON
        response = content.json()

        # Raise ValueError if token has expired
        if 'error' in response.keys():
            raise ValueError

    # Test token
    try:
        token_file_obj = open(TOKEN_PATH, 'rb')
        token_saved = pickle.load(token_file_obj)
        token_file_obj.close()
        token_header = token_saved.get('token_header')
        if test:
            test_token(t=token_header)
        return token_header

    # Expired Token
    except ValueError:
        return authenticate()

    # Token files not found
    except FileNotFoundError:
        return authenticate()
