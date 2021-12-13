# TD Ameritrade API Authentication

import pickle
import time
import urllib.parse
from pathlib import Path

import requests
from selenium import webdriver

from config import client_id, redirect_uri
from ..logger import TDALogger


# Set up loggers
auth_logger = TDALogger("auth").logger

# Chrome Driver Path
chromedriver_path = Path.joinpath(Path(__file__).parent.parent.parent.parent, Path('drivers/chromedriver.exe'))
temp_dir = Path.joinpath(Path(__file__).parent.parent, Path('temp/'))

# token.pickle path
token_path = Path.joinpath(temp_dir, 'token.pickle')
status_path = Path.joinpath(temp_dir, 'tda_status.pickle')


# Update status wait and time values
def update_wait_status(condition: bool = False):
    with open(status_path, 'wb') as status_obj:
        pickle.dump({"wait": condition,
                     "time": time.time()}, status_obj)
        status_obj.close()


# Get API status cache and wait based on status
def get_status_cache(wait: bool = True):
    while True:
        with open(status_path, 'rb') as status_obj:
            status_data = pickle.load(status_obj)
            wait_status = status_data.get("wait")
            time_status = status_data.get("time")
            status_obj.close()

        # Discredit status if last updated over 60 seconds ago
        if time.time() - time_status > 60:
            update_wait_status(False)

        # Wait
        if wait_status and wait:
            time.sleep(0.5)
        elif wait_status and not wait:
            return True
        else:
            return False


# Create temp files
def create_temp_files():
    for file_path in [token_path, status_path]:
        if not file_path.exists():
            # Create temp folder if it doesn't exist
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Create temp .pickle files
            with open(file_path, 'wb') as file_obj:
                pickle.dump({}, file_obj)
                file_obj.close()

            # Initiate status as False
            if file_path == status_path:
                update_wait_status(False)


# OAuth app
def authenticate():
    # Gets oauth code
    def parseurl():
        # Log in to TDA
        # define the components to build a URL
        method = 'GET'
        url = 'https://auth.tdameritrade.com/auth?'
        client_code = client_id + '@AMER.OAUTHAP'
        auth_payload = {'response_type': 'code',
                        'redirect_uri': redirect_uri,
                        'client_id': client_code}

        # build the URL
        auth_url = requests.Request(method, url, params=auth_payload).prepare().url

        # Set up and open url in Selenium Chrome browser with version error checking
        try:
            browser = webdriver.Chrome(executable_path=chromedriver_path)
            browser.get(auth_url)
        except Exception as E:
            if "version" in str(E):
                raise ValueError("Chromedriver version mismatch")
            else:
                raise ValueError(E)

        # Wait for Log in authentication
        while True:
            # Get current url
            current_url = browser.current_url
            # if url has 'code='
            if len(current_url.split('code=')) > 1:

                # Close browser
                browser.quit()

                # Parse url
                parse_url = urllib.parse.unquote(current_url.split('code=')[1])

                # log
                auth_logger.info('OAuth Log In Successful')

                return parse_url
            else:
                continue

    # Get oAuth access code
    oauth_url = r'https://api.tdameritrade.com/v1/oauth2/token'
    oauth_headers = {"Content-type": r'application/x-www-form-urlencoded'}

    # OAuth Payload
    # Use refresh to generate access token
    try:
        token_obj = open(token_path, 'rb')
        token_saved = pickle.load(token_obj)
        refresh_token_saved = token_saved.get('refresh_token')
        token_obj.close()

        oauth_payload = {'grant_type': 'refresh_token',
                         'refresh_token': refresh_token_saved,
                         'client_id': client_id}

        # Post oAuth data and get token
        oauth_post = requests.post(oauth_url, headers=oauth_headers, data=oauth_payload)

        # Get access token
        access_token = oauth_post.json()['access_token']

        # Format access_token
        token_header = {'Authorization': "Bearer {}".format(access_token)}

        # Save token
        with open(token_path, 'wb') as token_obj:
            # Format output dict
            token_saved.update({'token_header': token_header})
            # Save to pickle
            pickle.dump(token_saved, token_obj)
            token_obj.close()

        # Log
        auth_logger.info('OAuth performed using refresh token.')

    except Exception as error:
        auth_logger.error("Error authenticating using refresh code: " + str(error))

        # Create temp files
        create_temp_files()

        oauth_payload = {'grant_type': 'authorization_code',
                         'access_type': 'offline',
                         'code': parseurl(),
                         'client_id': client_id,
                         'redirect_uri': redirect_uri}

        # Post oAuth data and get token
        # TODO: Chromedriver version error
        oauth_post = requests.post(oauth_url, headers=oauth_headers, data=oauth_payload)

        # Get refresh and access token
        refresh_token = oauth_post.json()['refresh_token']
        access_token = oauth_post.json()['access_token']

        # Format access_token
        token_header = {'Authorization': "Bearer {}".format(access_token)}

        # Log
        auth_logger.info('OAuth performed using authorization code.')

        # Read tokens
        with open(token_path, 'rb') as token_obj:
            token_saved = pickle.load(token_obj)
            token_obj.close()

        # Save tokens
        with open(token_path, 'wb') as token_obj:
            # Format output dict
            token_saved.update({'token_header': token_header})
            token_saved.update({'refresh_token': refresh_token})
            # Save to pickle
            pickle.dump(token_saved, token_obj)
            token_obj.close()

    return token_header
