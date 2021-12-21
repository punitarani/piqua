# TD Ameritrade API Authentication
import os
import pickle
import time
import urllib.parse
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from config import client_id, redirect_uri, host
from ..logger import TDALogger

# Set up loggers
auth_logger = TDALogger("auth").logger

# Chrome Driver Path
CHROMEDRIVER = Path.joinpath(Path(__file__).parent.parent.parent.parent, Path('drivers/chromedriver.exe'))
TEMP_DIR = Path.joinpath(Path(__file__).parent.parent, Path('temp/'))

# token.pickle path
TOKEN_PATH = Path.joinpath(TEMP_DIR, 'token.pickle')
STATUS_PATH = Path.joinpath(TEMP_DIR, 'tda_status.pickle')


# Update status wait and time values
def update_wait_status(condition: bool = False):
    with open(STATUS_PATH, 'wb') as status_obj:
        pickle.dump({"wait": condition,
                     "time": time.time()}, status_obj)
        status_obj.close()


# Get API status cache and wait based on status
def get_status_cache(wait: bool = True):
    while True:
        with open(STATUS_PATH, 'rb') as status_obj:
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
    for file_path in [TOKEN_PATH, STATUS_PATH]:
        if not file_path.exists():
            # Create temp folder if it doesn't exist
            TEMP_DIR.mkdir(parents=True, exist_ok=True)

            # Create temp .pickle files
            with open(file_path, 'wb') as file_obj:
                pickle.dump({}, file_obj)
                file_obj.close()

            # Initiate status as False
            if file_path == STATUS_PATH:
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
            browser = webdriver.Chrome(executable_path=CHROMEDRIVER)
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
        token_obj = open(TOKEN_PATH, 'rb')
        token_saved = pickle.load(token_obj)
        refresh_token_saved = token_saved.get('refresh_token')
        token_obj.close()

        oauth_payload = {'grant_type': 'refresh_token',
                         'refresh_token': refresh_token_saved,
                         'client_id': client_id}

        # Post oAuth data and get token
        oauth_post = requests.post(oauth_url, headers=oauth_headers, data=oauth_payload)

        # Get access token
        # Error handle corrupt token.pickle file
        try:
            access_token = oauth_post.json()['access_token']
        except KeyError:
            auth_logger.error("token.pickle file is corrupted.")
            auth_logger.info("Renaming corrupted token.pickle file.")
            corrupted_token_path = os.path.join(TEMP_DIR, "token_corrupted.pickle")

            # Delete old corrupted token file
            if os.path.exists(corrupted_token_path):
                auth_logger.info("Deleting old corrupted token.pickle file.")
                os.remove(corrupted_token_path)

            os.rename(TOKEN_PATH, corrupted_token_path)

            # Raise FileNotFoundError to redirect to manual user authentication
            auth_logger.info("User authentication required.")
            raise FileNotFoundError

        # Format access_token
        token_header = {'Authorization': "Bearer {}".format(access_token)}

        # Save token
        with open(TOKEN_PATH, 'wb') as token_obj:
            # Format output dict
            token_saved.update({'token_header': token_header})
            # Save to pickle
            pickle.dump(token_saved, token_obj)
            token_obj.close()

        # Log
        auth_logger.info('OAuth performed using refresh token.')

    # User authentication by logging in
    except FileNotFoundError:
        auth_logger.error("Error authenticating using refresh code: token.pickle file is missing.")

        # Create temp files
        create_temp_files()

        oauth_payload = {'grant_type': 'authorization_code',
                         'access_type': 'offline',
                         'code': parseurl(),
                         'client_id': client_id,
                         'redirect_uri': redirect_uri}

        # Post oAuth data and get token
        oauth_post = requests.post(oauth_url, headers=oauth_headers, data=oauth_payload)

        # Get refresh and access token
        refresh_token = oauth_post.json()['refresh_token']
        access_token = oauth_post.json()['access_token']

        # Format access_token
        token_header = {'Authorization': "Bearer {}".format(access_token)}

        # Log
        auth_logger.info('OAuth performed using authorization code.')

        # Read tokens
        with open(TOKEN_PATH, 'rb') as token_obj:
            token_saved = pickle.load(token_obj)
            token_obj.close()

        # Save tokens
        with open(TOKEN_PATH, 'wb') as token_obj:
            # Format output dict
            token_saved.update({'token_header': token_header})
            token_saved.update({'refresh_token': refresh_token})
            # Save to pickle
            pickle.dump(token_saved, token_obj)
            token_obj.close()

    return token_header


class Authenticate:
    def __init__(self, override_mode: str = None, generate_new_refresh_token: bool = False):
        # User info
        self.redirect_uri = redirect_uri
        self.client_id = client_id

        # Set up logger
        self.logger = TDALogger("auth").logger

        # oauth variables
        self.oauth_url = r'https://api.tdameritrade.com/v1/oauth2/token'
        self.oauth_headers = {"Content-type": r'application/x-www-form-urlencoded'}

        # Mode
        if not override_mode:
            self.mode = host
        else:
            self.mode = override_mode

        if not self.test_token() or generate_new_refresh_token:
            self.token_header = self.main(mode=self.mode, force_user_auth=generate_new_refresh_token)
        else:
            self.token_header = self.read_token_file().get("token_header")

    # Main function
    def main(self, mode: str, force_user_auth: bool) -> dict:
        """
        :param force_user_auth: Forces user login to create new refresh token
        :param mode: "local" or "host". Decides if login url should be printed or opened in selenium
        :return: token_header
        """

        # Try to use local refresh code to generate
        if not force_user_auth:
            self.logger.debug("Authenticate with token file.")

            token = self.read_token_file()

            try:
                refresh_token = token.get("refresh_token")
                token_header = self.oauth(refresh_token=refresh_token)

            except KeyError:
                self.logger.error("Couldn't find refresh_token in token file")
                token_header = self.login_mode(mode=mode)

        else:
            token_header = self.login_mode(mode=mode)

        return token_header

    # Read local token file and return its contents
    def read_token_file(self) -> dict:
        self.logger.debug("Reading token.pickle file.")
        with open(TOKEN_PATH, "rb") as token:
            data = pickle.load(token)
            return data

    # Test if token has expired
    @staticmethod
    def test_token(token_header: dict = None) -> bool:
        if not token_header:
            with open(TOKEN_PATH, 'rb') as token_obj:
                token_saved = pickle.load(token_obj)

            token_header = token_saved.get('token_header')

        endpoint = r'https://api.tdameritrade.com/v1/userprincipals'
        content = requests.get(url=endpoint, headers=token_header)

        # User Principals JSON
        response = content.json()

        # Raise ValueError if token has expired
        if 'error' in response.keys():
            return False

        return True

    # Generate user login URL
    def generate_url(self) -> str:
        self.logger.debug("Generating user login URL with config credentials.")

        # define the components to build a URL
        method = 'GET'
        url = 'https://auth.tdameritrade.com/auth?'
        client_code = self.client_id + '@AMER.OAUTHAP'
        auth_payload = {'response_type': 'code',
                        'redirect_uri': self.redirect_uri,
                        'client_id': client_code}

        # build the URL
        auth_url = requests.Request(method, url, params=auth_payload).prepare().url

        # Log
        self.logger.debug("Generated user login url.")

        return auth_url

    # Get code from url after user logs in
    def parse_url(self, url: str) -> str:
        self.logger.debug("Parsing oauth code from url.")
        code = urllib.parse.unquote(url.split('code=')[1])
        return code

    # Logs in based on mode
    def login_mode(self, mode: str):
        if mode == "local":
            tkn_hdr = self.login()
        else:
            tkn_hdr = self.remote_login()

        return tkn_hdr

    # Local Mode: Opens user login url in selenium chrome browser
    def login(self, url: str = None) -> dict:
        self.logger.debug("Authenticate with user login.")

        # Generate url if not provided
        if not url:
            url = self.generate_url()

        # Set up and open url in Selenium Chrome browser with version error checking
        try:
            browser = webdriver.Chrome(executable_path=CHROMEDRIVER)
            browser.get(url)

        except WebDriverException:
            user_quit_msg = "User closed browser before login process completed."
            self.logger.error(user_quit_msg)
            raise ValueError(user_quit_msg)

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
            try:
                current_url_split = current_url.split('code=')

            except AttributeError:
                user_quit_msg = "User closed browser before login process completed."
                self.logger.error(user_quit_msg)
                raise ValueError(user_quit_msg)

            if len(current_url_split) > 1:
                # Close browser
                browser.quit()

                # Parse url to get code
                code = self.parse_url(url=current_url)

                # log
                auth_logger.info('OAuth Log In Successful')

            else:
                continue

            # Perform OAuth with code
            token_header = self.oauth(code=code)

            return token_header

    # Remote Mode: Print url and takes url input after logging in
    def remote_login(self, listen: bool = False) -> dict:
        self.logger.debug("Authenticate with remote login.")
        url = self.generate_url()

        self.logger.debug("Printed login url.")
        self.logger.debug("Waiting for user to input url with code after logging in.")

        # DO NOT LOG. ONLY PRINT
        print(f"\n\nLog in using: {url}")

        if listen:
            # Start server to listen to redirect url after logging in
            code = self.remote_listen()
        else:
            url_code = input("Please enter url after logging in: ")

            # Parse code form url
            code = self.parse_url(url=url_code)

        # Perform OAuth with code
        token_header = self.oauth(code=code)

        return token_header

    # POST auth code to create refresh and access token
    def oauth(self, code: str = None, refresh_token: str = None) -> dict:
        # Log
        if code:
            self.logger.debug("Performing OAuth with code.")
        elif refresh_token:
            self.logger.debug("Performing OAuth with refresh_token.")
        else:
            self.logger.error("Missing code and refresh_token params`1.")

        # Get oAuth access code
        oauth_payload = self.generate_oauth_payload(code=code, refresh_token=refresh_token)

        # Post oAuth data and get token
        self.logger.debug("Posting OAuth data.")
        oauth_post = requests.post(self.oauth_url, headers=self.oauth_headers, data=oauth_payload)
        print(oauth_post.json())

        # Get refresh and access token
        refresh_token = oauth_post.json()['refresh_token']
        access_token = oauth_post.json()['access_token']

        # Format access_token
        token_header = {'Authorization': "Bearer {}".format(access_token)}

        # Log
        auth_logger.info('OAuth performed successfully.')

        # Read token file
        token_saved = self.read_token_file()

        # Save or Update token file
        with open(TOKEN_PATH, 'wb') as token_obj:
            # Format output dict
            token_saved.update({'token_header': token_header})
            token_saved.update({'refresh_token': refresh_token})

            # Save to pickle
            pickle.dump(token_saved, token_obj)

            auth_logger.debug('Updated token.pickle file.')

        return token_header

    # Generate oauth payload from code
    def generate_oauth_payload(self, code: str = None, refresh_token: str = None) -> dict:

        # If code is given: uses code to generate refresh token and access token
        if code:
            payload = {'grant_type': 'authorization_code',
                       'access_type': 'offline',
                       'code': code,
                       'client_id': self.client_id,
                       'redirect_uri': self.redirect_uri}
            self.logger.debug("Generated OAuth payload with code.")
            return payload

        # If code is not given: generates payload to use local refresh token to generate access token
        elif refresh_token:
            payload = {'grant_type': 'refresh_token',
                       'refresh_token': refresh_token,
                       'client_id': client_id}
            self.logger.debug("Generated OAuth payload with refresh token.")
            return payload

        else:
            msg = "Error generating OAuth payload. Missing code or refresh_token"
            self.logger.error(msg)
            raise ValueError(msg)

    # Remote listen to redirect url after login. Outputs OAuth code
    # TODO: DO NOT USE. BUGGY
    def remote_listen(self) -> str:
        HOST = self.redirect_uri
        PORT = 8888

        host_split = HOST.split(":")
        if len(host_split) >= 3:
            HOST = host_split[1][2:]
            PORT = int(host_split[2])

        elif "://" in HOST:
            HOST = host_split[1][2:]

        self.logger.info(f"Attempting to start server at {HOST}:{PORT}")

        # Create a server socket, bind it to a port and start listening
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((HOST, PORT))
        serverSocket.listen(5)

        self.logger.info(f"Listening to {HOST}:{PORT}")

        cliSocket, address = serverSocket.accept()
        print('Received a connection from:', address)

        full_url_bytes = cliSocket.recv(4*1024)
        full_url = full_url_bytes.decode('ASCII')

        code = full_url.split("code=")[-1]
        code = code.split(" HTTP")[0]

        return code
