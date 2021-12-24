# TDA Stream Client

import asyncio
import copy
import inspect
import json
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlencode

import websockets
from websockets.extensions.permessage_deflate import ClientPerMessageDeflateFactory

from config import account_id
from .services import Fields
from ..account import Account
from ..logger import TDALogger

# Connected Webclient Sockets
client_socket = {}


class Handler:
    """
    Basic Stream Handler
    """

    def __init__(self, func: callable, fields: dict | Fields):
        self.func = func

        if isinstance(fields, Fields):
            self.fields = fields.value
        else:
            self.fields = fields

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def label_message(self, msg: list | dict):
        """
        Label the message with the fields
        :param msg: Stream Message
        :return:
        """

        """
        Example msg:
        [{"service":"LISTED_BOOK", "timestamp":1640371904385,"command":"SUBS",
        "content":[{"key":"SPY","1":1640307600996,"2":[],"3":[]},{"key":"IWM","1":1640307600959,"2":[],"3":[]}]}]
        """

        msg = copy.deepcopy(msg)

        if isinstance(msg, dict):
            msg = [msg]

        output = {}

        for data in msg:
            service = data.get("service")
            if 'content' in data:
                output_msg = {}

                for content in data.get("content"):
                    content_msg = {}

                    for field in content:
                        if field in self.fields.keys():
                            content_msg.update({self.fields.get(field): content.get(field)})

                        else:
                            content_msg.update({field: content.get(field)})

                    output_msg.update({content.get("key"): content_msg})
                output.update({service: output_msg})

            else:
                return output.update({service: data})

        return output


class StreamClient:
    """
    TDA Websocket Stream Client
    """

    def __init__(self):
        """
        Initialize Stream Client
        """
        self.logger = TDALogger(logger_name="StreamClient").logger

        # Account Variables
        self._account_id = account_id

        # Stream Client Variables
        self.userPrincipals = Account().user_principals().copy()[0]
        self._accounts = self.userPrincipals.loc["accounts"][0]
        self._streamer_url = self.userPrincipals.loc["streamerInfo.streamerSocketUrl"]
        self._streamer_key = self.userPrincipals.loc["streamerSubscriptionKeys.keys"][0]['key']
        self._streamer_appid = self.userPrincipals.loc["streamerInfo.appId"]
        self._token = self.userPrincipals.loc["streamerInfo.token"]

        # Stream Handlers
        self.handlers = defaultdict(list)

        # Async Variables
        self._lock = asyncio.Lock()

        # Request Variables
        self._request_id = 0

        # Web Socket Object
        self.Socket = None
        self._logged_in = False

    async def connect(self):
        """
        Create websockets client and establish connection to server
        :return: Socket
        """
        self.logger.info("Connecting to server")

        if self.Socket is None or "socket" not in client_socket:
            # Generate URL
            # ws_url = r"wss://streamer-ws.tdameritrade.com/ws"
            ws_url = f'wss://{str(self._streamer_url)}/ws'

            # Define websocket connect args
            websocket_connect_args = {"extensions": [ClientPerMessageDeflateFactory()]}

            # Connect to server with SSL
            socket = await websockets.connect(ws_url, **websocket_connect_args)

            # Store socket
            self.Socket = socket
            client_socket.update({"socket": socket})
            self.logger.info("Connected to server")

        else:
            socket = client_socket.get("socket")
            self.logger.info("Already connected to server")
            self.Socket = socket

        return self.Socket

    async def disconnect(self):
        """
        Disconnect from server
        :return: None
        """
        if self.Socket is not None:
            self.logger.info("Disconnecting from server")
            await self.Socket.close()
        else:
            self.logger.info("Not connected to server")

    async def send(self, msg) -> None:
        """
        Send message to server
        :param msg: Message to send
        :return: None
        """

        self.logger.debug(f"Sending message: {msg}")
        await self.Socket.send(json.dumps(msg))

    async def receive(self):
        """
        Receive message from server
        :return: Message
        """

        msg = await self.Socket.recv()
        # print(msg)
        return msg

    def _make_request(self,
                      service: str,
                      command: str,
                      params: dict) -> [dict, int]:
        """
        Build request dict and increment request id
        :param service: Service
        :param command: Command
        :param params:  Parameters
        :return: Request dict and Request ID
        """
        request_id = self._request_id
        self._request_id += 1

        request = {
            'service': service,
            'requestid': request_id,
            'command': command,
            'account': self._account_id,
            'source': self._streamer_appid,
            'parameters': params
        }

        return request, request_id

    async def await_response(self,
                             request_id: int | str,
                             service: str,
                             command: str) -> dict | bool:
        """
        Await response from server
        :param request_id: Request ID
        :param service: Service
        :param command: Command
        :return: Response
        """

        # Await response
        while True:
            responses = await self.receive()

            # Parse responses string to json dict
            responses = json.loads(responses)

            # Check if response is for this request
            if "response" in responses.keys():
                for response in responses.get("response"):
                    if response.get("requestid") == str(request_id):
                        if response.get("service") == service and response.get("command") == command:
                            return response.get("content")
                        else:
                            self.logger.warning(f"Received unexpected response: {response}")
                            return False

    async def handle_socket_disconnect(self) -> bool | None:
        """
        Handle message from server
        :return: None
        """

        # Await response
        messages = await self.receive()

        # Parse response string to json dict
        messages = json.loads(messages)

        if "notify" in messages.keys():
            for notify in messages.get("notify"):

                # Stream is Alive
                if "heartbeat" in notify.keys():
                    self.logger.debug(f"Socket is Alive. Received heartbeat: {notify.get('heartbeat')}")

                # Stream is Stopped
                elif notify.get("service") == "ADMIN":
                    self.logger.warning(f"Socket closed by TDA API. msg: {notify.get('content')}")
                    await self.disconnect()
                    self._logged_in = False
                    return True

    async def handle_message(self):
        async with self._lock:
            msg = await self.receive()

        # Parse response string to json dict
        msg = json.loads(msg)

        if "data" in msg.keys():
            for data in msg.get("data"):
                if data.get("service") in self.handlers.keys():

                    for handler in self.handlers.get(data.get("service")):
                        # Label Message
                        data = handler.label_message(data)

                        # Handle Message
                        h = handler(data)

                        # Schedule Message if awaitable
                        if inspect.isawaitable(h):
                            asyncio.ensure_future(h)

    async def service_request(self,
                              service: str,
                              command: str,
                              symbols: list = None,
                              fields: int = None):

        """
        Send service request to server
        :param service: Service
        :param command: Command
        :param symbols: List of Symbols
        :param fields:  Largest fields int
        :return:
        """

        # Build params keys:    Comma seperated string of symbols
        parameters = {'keys': ','.join(symbols)}

        # Build fields string:  Comma seperated string of ints upto fields
        if fields is not None:
            fields = ','.join(map(str, range(0, fields + 1)))
            parameters.update({"fields": fields})

        # Build request
        request, request_id = self._make_request(
            service=service, command=command,
            params=parameters)

        # Send request
        async with self._lock:
            await self.send({'requests': [request]})
            response = await self.await_response(request_id=request_id, service=service, command=command)

        return response

    # Login after connecting
    async def login(self):
        """
        Login to server
        :return: Socket
        """

        self._logged_in = True

        # Connect to ws server
        socket = await self.connect()

        # Build login request params
        timestamp = int(datetime.strptime(
            self.userPrincipals.loc["streamerInfo.tokenTimestamp"], '%Y-%m-%dT%H:%M:%S%z').timestamp()) * 1000

        credentials = {
            "userid": self._account_id,
            "token": self.userPrincipals.loc["streamerInfo.token"],
            "company": self._accounts.get("company"),
            "segment": self._accounts.get("segment"),
            "cddomain": self._accounts.get("accountCdDomainId"),
            "usergroup": self.userPrincipals.loc["streamerInfo.userGroup"],
            "accesslevel": self.userPrincipals.loc["streamerInfo.accessLevel"],
            "authorized": "Y",
            "timestamp": timestamp,
            "appid": self._streamer_appid,
            "acl": self.userPrincipals.loc["streamerInfo.acl"]
        }

        request_params = {
            'credential': urlencode(credentials),
            'token': self._token,
            'version': '1.0'
        }

        """
        Format:
        

        request = {
            "requests": [
                {
                    "service": "ADMIN",
                    "command": "LOGIN",
                    "requestid": 0,
                    "account": self._account_id,
                    "source": self._streamer_appid,
                    "parameters": {
                        "credential": urlencode(credentials),
                        "token": self._token,
                        "version": "1.0"
                    }
                }
            ]
        }
        """

        request, request_id = self._make_request(service="ADMIN", command="LOGIN", params=request_params)

        # Send and Wait for Response
        async with self._lock:
            self.logger.info("Sending login request")
            await self.send({'requests': [request]})
            response = await self.await_response(request_id=request_id, service="ADMIN", command="LOGIN")

        if isinstance(response, dict) and response.get("code") == 0:
            self.logger.info(f"Login successful. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Login failed. Response: {response}")

    # Logout and disconnect
    async def logout(self, disconnect: bool = True):
        service = "ADMIN"
        command = "LOGOUT"

        if self._logged_in:
            request, request_id = self._make_request(service=service, command=command, params={})

            # Send and Wait for Response
            async with self._lock:
                self.logger.info("Sending Logout request")
                await self.send({'requests': [request]})
                response = await self.await_response(request_id=request_id, service=service, command=command)

            if response.get("code") == 0:
                self.logger.info(f"Logout SUCCESS. msg: {response.get('msg')}")
                self._logged_in = False
            else:
                self.logger.error(f"Logout FAILED. Response: {response}")

        else:
            self.logger.info("Not logged in. No need to logout")

        if disconnect:
            await self.disconnect()

    ####################################################################################################################
    # ACCT_ACTIVITY
    async def account_activity_sub(self):
        """
        Subscribe to account activity
        """
        service = "ACCT_ACTIVITY"
        command = "SUBS"

        _request, request_id = self._make_request(service=service, command=command, params={})

        request = {
            "requests": [
                {
                    "service": service,
                    "requestid": str(request_id),
                    "command": command,
                    "account": str(self._account_id),
                    "source": str(self._streamer_appid),
                    "parameters": {
                        "keys": str(self._streamer_key),
                        "fields": "0,1,2,3"
                    }
                }
            ]
        }

        async with self._lock:
            await self.send(request)
            response = await self.await_response(request_id, service, command)

        if response.get("code") == 0:
            self.logger.info(f"Account Activity Subscription SUCCESS. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Account Activity Subscription FAILED. Response: {response}")

    async def account_activity_unsub(self):
        """
        Unsubscribe to account activity
        """
        service = "ACCT_ACTIVITY"
        command = "UNSUBS"

        _request, request_id = self._make_request(service=service, command=command, params={})

        request = {
            "requests": [
                {
                    "service": service,
                    "requestid": str(request_id),
                    "command": command,
                    "account": str(self._account_id),
                    "source": str(self._streamer_appid),
                    "parameters": {
                        "keys": str(self._streamer_key),
                        "fields": "0,1,2,3"
                    }
                }
            ]
        }

        async with self._lock:
            await self.send(request)
            response = await self.await_response(request_id, service, command)

        if response.get("code") == 0:
            self.logger.info(f"Account Activity Unsubscription SUCCESS. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Account Activity Unsubscription FAILED. Response: {response}")

    def add_account_activity_handler(self, handler: callable):
        self.handlers["ACCT_ACTIVITY"].append(Handler(handler, Fields.account_activity_fields))

    def remove_account_activity_handler(self, handler: callable):
        self.handlers["ACCT_ACTIVITY"].remove(Handler(handler, Fields.account_activity_fields))

    ####################################################################################################################
    # Level One
    # QUOTE

    # ------------------------------------------------------------------------------------------------------------------
    # OPTION

    # ------------------------------------------------------------------------------------------------------------------
    # LEVELONE_FUTURES

    # ------------------------------------------------------------------------------------------------------------------
    # LEVELONE_FUTURES_OPTIONS

    ####################################################################################################################

    # Level 2 Book
    # LISTED_BOOK
    async def level_two_listed_sub(self, symbols: str | list):
        """
        Subscribe to Level 2 NYSE, AMEX Symbols
        :param symbols: Symbol or list of symbols to Subscribe to
        :return: None
        """
        service = "LISTED_BOOK"
        command = "SUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=3)
        if response.get("code") == 0:
            self.logger.info(f"L2 Subscription SUCCESS. Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"L2 Subscription FAILED. Symbols: {symbols}. Response: {response}")

    async def level_two_listed_unsub(self, symbols: str | list):
        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service="LISTED_BOOK",
                                              command="UNSUBS")
        if response.get("code") == 0:
            self.logger.info(f"L2 Unsubscription SUCCESS. Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"L2 Unsubscription FAILED. Symbols: {symbols}. Response: {response}")

    def add_level_two_listed_handler(self, handler: callable):
        self.handlers["LISTED_BOOK"].append(Handler(handler, Fields.level_two_fields))

    def remove_level_two_listed_handler(self, handler: callable):
        self.handlers["LISTED_BOOK"].remove(Handler(handler, Fields.level_two_fields))

    # ------------------------------------------------------------------------------------------------------------------
    # NASDAQ_BOOK

    # ------------------------------------------------------------------------------------------------------------------
    # OPTIONS_BOOK

    # ------------------------------------------------------------------------------------------------------------------
    # FUTURES_BOOK

    # ------------------------------------------------------------------------------------------------------------------
    # FUTURES_OPTIONS_BOOK

    ####################################################################################################################

    # TimeSale
    # TIMESALE_EQUITY

    # ------------------------------------------------------------------------------------------------------------------
    # TIMESALE_OPTIONS

    # ------------------------------------------------------------------------------------------------------------------
    # TIMESALE_FUTURES

    ####################################################################################################################

    # News
    # NEWS_HEADLINE

    # ------------------------------------------------------------------------------------------------------------------
    # NEWS_STORY

    # ------------------------------------------------------------------------------------------------------------------
    # NEWS_HEADLINE_LIST

    ####################################################################################################################
