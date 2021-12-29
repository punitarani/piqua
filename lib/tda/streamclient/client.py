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
from .services import Fields, QOS
from ..account import Account
from ..logger import TDALogger

# Connected Webclient Sockets
client_socket = {}


class JSONDecode:
    def __init__(self, msg):
        """
        JSONDecode class constructor
        :param msg: message to decode
        """
        self.logger = TDALogger("Stream Client").logger

    def __new__(cls, msg) -> dict:
        """
        Return decoded message when Class is instantiated
        :param msg: Message to decode
        """
        return cls.decode(msg=msg)

    @staticmethod
    def decode(msg=None) -> dict:
        """
        Decode message
        :param msg: Message to decode
        :return: Decoded message as dict
        """
        logger = TDALogger("Stream Client").logger

        try:
            return json.loads(msg)
        except Exception as err:
            logger.error(f"{err} while decoding msg: ", msg)
            return json.loads(msg, strict=False)


class Handler:
    """
    Basic Stream Handler
    """

    def __init__(self, func: callable, fields: dict | Fields):
        self.func = func
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
        
        service = 'LISTED_BOOK'
        
        content = {"key":"SPY","1":1640307600996,"2":[],"3":[]}
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

                    for field in content.keys():
                        if field in self.fields.keys():
                            content_msg.update({self.fields.get(field): content.get(field)})

                        else:
                            content_msg.update({field: content.get(field)})

                    output_msg.update({content.get("key"): content_msg})
                output.update({service: output_msg})

            else:
                return output.update({service: data})

        return output


class BookHandler(Handler):
    """
    Handler class for Book Stream
    """

    def label_message(self, msg: list | dict):
        """
        Label the message with the fields
        :param msg: Stream Message
        :return:
        """

        # Relabel top-level fields
        msg = super().label_message(msg).copy()

        """
        Output Examples:
        msg
        {'LISTED_BOOK': {'SPY': {'key': 'SPY', 'BOOK_TIME': 1640653200830, 'BIDS': [{'0': 476.91, '1': 700, '2': 2, 
        '3': [{'0': 'ARCX', '1': 500, '2': 68388307}, {'0': 'CINN', '1': 200, '2': 68388306}]}], 'ASKS': [{'0': 
        476.98, '1': 500, '2': 1, '3': [{'0': 'ARCX', '1': 500, '2': 68391101}]}, {'0': 476.99, '1': 200, '2': 1, 
        '3': [{'0': 'CINN', '1': 200, '2': 68400012}]}]}, 'BABA': {'key': 'BABA', 'BOOK_TIME': 1640653200830, 
        'BIDS': [{'0': 116.66, '1': 400, '2': 1, '3': [{'0': 'ARCX', '1': 400, '2': 68169737}]}, {'0': 116.5, 
        '1': 200, '2': 1, '3': [{'0': 'AMEX', '1': 200, '2': 67643382}]}], 'ASKS': [{'0': 116.95, '1': 200, '2': 1, 
        '3': [{'0': 'ARCX', '1': 200, '2': 68390430}]}, {'0': 117.1, '1': 100, '2': 1, '3': [{'0': 'AMEX', '1': 100, 
        '2': 66007842}]}]}}}
        
        data
        {'SPY': {'key': 'SPY', 'BOOK_TIME': 1640653200830, 'BIDS': [{'0': 476.91, '1': 700, '2': 2, 
        '3': [{'0': 'ARCX', '1': 500, '2': 68388307}, {'0': 'CINN', '1': 200, '2': 68388306}]}], 'ASKS': [{'0': 
        476.98, '1': 500, '2': 1, '3': [{'0': 'ARCX', '1': 500, '2': 68391101}]}, {'0': 476.99, '1': 200, '2': 1, 
        '3': [{'0': 'CINN', '1': 200, '2': 68400012}]}]}, 'BABA': {'key': 'BABA', 'BOOK_TIME': 1640653200830, 
        'BIDS': [{'0': 116.66, '1': 400, '2': 1, '3': [{'0': 'ARCX', '1': 400, '2': 68169737}]}, {'0': 116.5, 
        '1': 200, '2': 1, '3': [{'0': 'AMEX', '1': 200, '2': 67643382}]}], 'ASKS': [{'0': 116.95, '1': 200, '2': 1, 
        '3': [{'0': 'ARCX', '1': 200, '2': 68390430}]}, {'0': 117.1, '1': 100, '2': 1, '3': [{'0': 'AMEX', '1': 100, 
        '2': 66007842}]}]}}
        
        bid_ask_data
        {'key': 'SPY', 'BOOK_TIME': 1640653200830, 'BIDS': [{'0': 476.91, '1': 700, '2': 2, 
        '3': [{'0': 'ARCX', '1': 500, '2': 68388307}, {'0': 'CINN', '1': 200, '2': 68388306}]}], 'ASKS': [{'0': 
        476.98, '1': 500, '2': 1, '3': [{'0': 'ARCX', '1': 500, '2': 68391101}]}, {'0': 476.99, '1': 200, '2': 1, 
        '3': [{'0': 'CINN', '1': 200, '2': 68400012}]}]}
        
        Bids/Asks [{'0': 476.91, '1': 700, '2': 2, '3': [{'0': 'ARCX', '1': 500, '2': 68388307}, {'0': 'CINN', 
        '1': 200, '2': 68388306}]}] """

        services = list(set(msg.keys()))

        if len(services) > 1:
            logger = StreamClient().logger
            logger.error(f"Found more than one service in msg: {msg}")
            logger.info(f"Continuing with the first service: {services[0]}")

        service = services[0]

        exchange_fields = Fields.book_exchange
        bids_asks = ["bids", "Asks"]

        data = msg.get(service)
        tickers = data.keys()

        new_data = {}

        # Ticker
        for ticker in tickers:
            ticker_data = data.get(ticker)
            ticker_data_keys = ticker_data.keys()
            new_ticker_data = {}

            # Bid/Ask
            for bid_ask in bids_asks:
                if bid_ask in ticker_data_keys:
                    new_bid_data = []

                    for bid_ask_data in ticker_data.get(bid_ask):
                        new_bid_ask = {}

                        # Update first level fields
                        for field in bid_ask_data.keys():

                            # Update exchange field keys
                            if field == "3":
                                bid_ask_exchange = []

                                for exchange in bid_ask_data.get("3"):
                                    exchange_msg = {}

                                    for e_fields in exchange.keys():
                                        if e_fields in exchange_fields.keys():
                                            exchange_msg.update(
                                                {exchange_fields.get(e_fields): exchange.get(e_fields)})
                                        else:
                                            exchange_msg.update({e_fields: exchange.get(e_fields)})

                                    bid_ask_exchange.append(exchange_msg)

                                new_bid_ask.update({self.fields.get(field): bid_ask_exchange})

                            # Update other fields
                            elif field in self.fields.keys():
                                new_bid_ask.update({self.fields.get(field): bid_ask_data.get(field)})
                            else:
                                new_bid_ask.update({field: bid_ask_data.get(field)})

                        new_bid_data.append(new_bid_ask)

                    new_ticker_data.update({ticker: new_bid_data})

            new_data.update({ticker: new_ticker_data})

        return {service: new_data}


class StreamClient:
    """
    TDA Websocket Stream Client

    Endpoints:
        Account:
            Activity

            Quality of Service



        Level One:
            Equity

            Equity Options

            Futures

            Futures Options (DOES NOT WORK)


        Book (L2):
            Equity

            Equity Options

            Futures (DOWN)

            Futures Options (DOES NOT WORK)


        TimeSale:
            Equity

            Equity Options (DOES NOT WORK)

            Futures


        News:
            Headline

    Application:
        1. Initialize StreamClient(): Login
        2. Add/Remove Services and Handlers:
            1. Services: Subscribe to TDA relevant services to get data

            2. Handlers: Add application relevant handlers to manipulate data
        3. Close Socket: Logout -> Disconnect(Optional)

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
            responses = JSONDecode.decode(responses)

            # Check if response is for this request
            if "response" in responses.keys():
                for response in responses.get("response"):
                    if response.get("requestid") == str(request_id):
                        if response.get("service") == service and response.get("command") == command:
                            return response.get("content")
                        else:
                            self.logger.warning(f"Received unexpected response: {response}")
                            return False

    async def handle_message(self):
        """
        Handle message from server
        """
        async with self._lock:
            msg = await self.receive()

        # Parse response string to json dict
        msg = JSONDecode.decode(msg)

        if "data" in msg.keys():
            for data in msg.get("data"):

                if data.get("service") in self.handlers.keys():
                    for handler in self.handlers.get(data.get("service")):
                        # Label Message
                        labelled_data = handler.label_message(data)

                        # Handle Message
                        h = handler(msg=labelled_data)

                        # Schedule Message if awaitable
                        if inspect.isawaitable(h):
                            asyncio.ensure_future(h)

        if "notify" in msg.keys():
            for data in msg.get("notify"):

                # Stream is Alive
                if "heartbeat" in data.keys():
                    continue

                # Stream is Stopped
                elif data.get("service") == "ADMIN":
                    self.logger.warning(f"Socket closed by TDA API. msg: {data.get('content')}")
                    await self.disconnect()
                    self._logged_in = False

                else:
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
        await self.connect()

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
        self.handlers["ACCT_ACTIVITY"].append(Handler(handler, Fields.account_activity))

    def remove_account_activity_handler(self, handler: callable):
        self.handlers["ACCT_ACTIVITY"].remove(Handler(handler, Fields.account_activity))

    # -------------------------------------------------------------------------------------------------------------------

    # QOS Update
    async def update_QOS(self, level: str | QOS):
        """
        Update Quality of Service: rates of data updates per protocol
        :param level: QOS Level: '0'(fastest)-'5'
        :return: None
        """

        if isinstance(level, QOS):
            level = level.value

        service = "ADMIN"
        command = "QOS"
        params = {
            "qoslevel": level
        }

        request, request_id = self._make_request(service=service, command=command, params=params)

        # Send and Wait for Response
        async with self._lock:
            self.logger.info("Sending QOS update request")
            await self.send({'requests': [request]})
            response = await self.await_response(request_id=request_id, service=service, command=command)

        if response.get("code") == 0:
            self.logger.info(f"QOS update SUCCESS. Updated to: {level}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"QOS update FAILED. Response: {response}")

    ####################################################################################################################
    # Level One
    # QUOTE
    async def level_one_equity_sub(self, symbols: str | list):
        """
        Subscribe to Level One Equity Quote
        :param symbols: Symbol or list of symbols to subscribe to
        :return: None
        """

        service = "QUOTE"
        command = "SUBS"
        fields = 52

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"L1 Equity Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"L1 Equity Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def level_one_equity_unsub(self, symbols: str | list):
        """
        Unsubscribe to level one equity
        :param symbols: Symbol or list of symbols
        :return: None
        """

        service = "QUOTE"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"L1 Equity Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"L1 Equity Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_level_one_equity_handler(self, handler: callable):
        self.handlers["QUOTE"].append(Handler(handler, Fields.level_one_equity))

    def remove_level_one_equity_handler(self, handler: callable):
        self.handlers["QUOTE"].remove(Handler(handler, Fields.level_one_equity))

    # ------------------------------------------------------------------------------------------------------------------
    # OPTION
    async def level_one_options_sub(self, symbols: str | list):
        """
        Subscribe to Level One Options
        :param symbols: Symbol or list of symbols to subscribe to
        :return: None
        """
        service = "OPTION"
        command = "SUBS"
        fields = 41

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"L1 Options Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"L1 Options Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def level_one_options_unsub(self, symbols: str | list):
        service = "OPTION"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"L1 Options Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"L1 Options Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_level_one_options_handler(self, handler: callable):
        self.handlers["OPTION"].append(Handler(handler, Fields.level_one_options))

    def remove_level_one_options_handler(self, handler: callable):
        self.handlers["OPTION"].remove(Handler(handler, Fields.level_one_options))

    # ------------------------------------------------------------------------------------------------------------------
    # LEVELONE_FUTURES
    async def level_one_futures_sub(self, symbols: str | list):
        """
        Subscribe to Level One Futures data.
        :param symbols: Symbol or list of symbols to subscribe to.
        :return: None
        """
        service = "LEVELONE_FUTURES"
        command = "SUBS"
        fields = 35

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"L1 Futures Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"L1 Futures SubscriptionFAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def level_one_futures_unsub(self, symbols: str | list):
        service = "LEVELONE_FUTURES"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"L1 Futures Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"L1 Futures Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_level_one_futures_handler(self, handler: callable):
        self.handlers["LEVELONE_FUTURES"].append(Handler(handler, Fields.level_one_futures))

    def remove_level_one_futures_handler(self, handler: callable):
        self.handlers["LEVELONE_FUTURES"].remove(Handler(handler, Fields.level_one_futures))

    # ------------------------------------------------------------------------------------------------------------------
    # LEVELONE_FUTURES_OPTIONS
    async def level_one_futures_options_sub(self, symbols: str | list):
        """
        Subscribe to Level One Futures Options
        :param symbols: Symbols or list of symbols to subscribe to
        :return: None
        """

        service = "LEVELONE_FUTURES_OPTIONS"
        command = "SUBS"
        fields = 35

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"L1 Futures Options Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"L1 Futures Options Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def level_one_futures_options_unsub(self, symbols: str | list):
        service = "LEVELONE_FUTURES_OPTIONS"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"L1 Futures Options Unsubscription SUCCESS."
                             f"Symbols: {symbols}."
                             f"msg: {response.get('msg')}")
        else:
            self.logger.error(f"L1 Futures Options Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_level_one_futures_options_handler(self, handler: callable):
        self.handlers["LEVELONE_FUTURES_OPTIONS"].append(Handler(handler, Fields.level_one_futures))

    def remove_level_one_futures_options_handler(self, handler: callable):
        self.handlers["LEVELONE_FUTURES_OPTIONS"].remove(Handler(handler, Fields.level_one_futures))

    ####################################################################################################################

    # Level 2 Book
    # LISTED_BOOK
    async def listed_book_sub(self, symbols: str | list):
        """
        Subscribe to Level 2 NYSE, AMEX Stocks
        :param symbols: Symbol or list of symbols to Subscribe to
        :return: None
        """

        service = "LISTED_BOOK"
        command = "SUBS"
        fields = 3

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"Listed Book Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Listed Book Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def listed_book_unsub(self, symbols: str | list):
        """
        Unsubscribe to Level 2 NYSE, AMEX Stocks
        :param symbols: Symbol or list of symbols to Unsubscribe to
        :return: None
        """

        service = "LISTED_BOOK"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"Listed Book Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Listed Book Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_listed_book_handler(self, handler: callable):
        self.handlers["LISTED_BOOK"].append(BookHandler(handler, Fields.book))

    def remove_listed_book_handler(self, handler: callable):
        self.handlers["LISTED_BOOK"].remove(BookHandler(handler, Fields.book))

    # ------------------------------------------------------------------------------------------------------------------
    # NASDAQ_BOOK
    async def nasdaq_book_sub(self, symbols: str | list):
        """
        Subscribe to Level 2 NASDAQ Stocks
        :param symbols: Symbol or list of symbols to Subscribe to
        :return: None
        """

        service = "NASDAQ_BOOK"
        command = "SUBS"
        fields = 3

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"NASDAQ Book Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"NASDAQ Book Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def nasdaq_book_unsub(self, symbols: str | list):
        """
        Unsubscribe to Level 2 NASDAQ Stocks
        :param symbols: Symbol or list of symbols to Unsubscribe from
        :return: None
        """

        service = "NASDAQ_BOOK"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"NASDAQ Book Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"NASDAQ Book Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_nasdaq_book_handler(self, handler: callable):
        self.handlers["NASDAQ_BOOK"].append(BookHandler(handler, Fields.book))

    def remove_nasdaq_book_handler(self, handler: callable):
        self.handlers["NASDAQ_BOOK"].remove(BookHandler(handler, Fields.book))

    # ------------------------------------------------------------------------------------------------------------------
    # OPTIONS_BOOK
    async def options_book_sub(self, symbols: str | list):
        """
        Subscribe to Level 2 Equity Options
        :param symbols: Options Symbol or list of symbols to Subscribe to
        :return: None
        """

        service = "OPTIONS_BOOK"
        command = "SUBS"
        fields = 3

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"Options Book Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Options Book Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def options_book_unsub(self, symbols: str | list):
        """
        Unsubscribe from Level 2 Equity Options
        :param symbols: Equity Options Symbol or list of symbols to Unsubscribe from
        :return: None
        """

        service = "OPTIONS_BOOK"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)
        if response.get("code") == 0:
            self.logger.info(f"Options Book Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Options Book Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_options_book_handler(self, handler: callable):
        self.handlers["OPTIONS_BOOK"].append(BookHandler(handler, Fields.book))

    def remove_options_book_handler(self, handler: callable):
        self.handlers["OPTIONS_BOOK"].remove(BookHandler(handler, Fields.book))

    # ------------------------------------------------------------------------------------------------------------------
    # FUTURES_BOOK
    async def futures_book_sub(self, symbols: str | list):
        """
        Subscribe to Level 2 Futures
        :param symbols: Futures Symbol or list of symbols to Subscribe to
        :return: None
        """

        service = "FUTURES_BOOK"
        command = "SUBS"
        fields = 3

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"Futures Book Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Futures Book Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def futures_book_unsub(self, symbols: str | list):
        """
        Unsubscribe from Level 2 Futures
        :param symbols: Futures Symbol or list of symbols to Unsubscribe from
        :return:
        """

        service = "FUTURES_BOOK"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"Futures Book Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Futures Book Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_futures_book_handler(self, handler: callable):
        self.handlers["FUTURES_BOOK"].append(BookHandler(handler, Fields.book))

    def remove_futures_book_handler(self, handler: callable):
        self.handlers["FUTURES_BOOK"].remove(BookHandler(handler, Fields.book))

    # ------------------------------------------------------------------------------------------------------------------
    # FUTURES_OPTIONS_BOOK
    async def futures_options_book_sub(self, symbols: str | list):
        """
        Subscribe to Level 2 Equity Options
        :param symbols: Equity Options Symbol or list of symbols to Subscribe to
        :return: None
        """

        service = "FUTURES_OPTIONS_BOOK"
        command = "SUBS"
        fields = 3

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"Futures Options Book Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Futures Options Book Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def futures_options_book_unsub(self, symbols: str | list):
        """
        Unsubscribe to Level 2 Equity Options
        :param symbols: Equity Options Symbol or list of symbols to Unsubscribe from
        :return: None
        """

        service = "FUTURES_BOOK"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"Futures Options Book Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Futures Options Book Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_futures_options_book_handler(self, handler: callable):
        self.handlers["FUTURES_OPTIONS_BOOK"].append(BookHandler(handler, Fields.book))

    def remove_futures_options_book_handler(self, handler: callable):
        self.handlers["FUTURES_OPTIONS_BOOK"].remove(BookHandler(handler, Fields.book))

    ####################################################################################################################

    # TimeSale
    # TIMESALE_EQUITY
    async def timesale_equity_sub(self, symbols: str | list):
        """
        Subscribe to Level 2 Equity
        :param symbols: Symbol or list of symbols to Subscribe to
        :return: None
        """

        service = "TIMESALE_EQUITY"
        command = "SUBS"
        fields = 4

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"Equity TimeSale Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Equity TimeSale Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def timesale_equity_unsub(self, symbols: str | list):
        """
        Unsubscribe to Level 2 Equity
        :param symbols: Equity Symbol or list of symbols to Unsubscribe from
        :return: None
        """

        service = "TIMESALE_EQUITY"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"Equity TimeSale Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Equity TimeSale Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_timesale_equity_handler(self, handler: callable):
        self.handlers["TIMESALE_EQUITY"].append(Handler(handler, Fields.timesale))

    def remove_timesale_equity_handler(self, handler: callable):
        self.handlers["TIMESALE_EQUITY"].remove(Handler(handler, Fields.timesale))

    # ------------------------------------------------------------------------------------------------------------------
    # TIMESALE_OPTIONS
    async def timesale_options_sub(self, symbols: str | list):
        """
        Unsubscribe to Level 2 Equity
        :param symbols: Symbol or list of symbols to Unsubscribe to
        :return: None
        """

        service = "TIMESALE_OPTIONS"
        command = "SUBS"
        fields = 4

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"Options TimeSale Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Options TimeSale Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def timesale_options_unsub(self, symbols: str | list):
        """
        Unsubscribe to Level 2 Timesale
        :param symbols: Options Symbol or list of symbols to Unsubscribe from
        :return: None
        """

        service = "TIMESALE_OPTIONS"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"Options TimeSale Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Options TimeSale Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_timesale_options_handler(self, handler: callable):
        self.handlers["TIMESALE_OPTIONS"].append(Handler(handler, Fields.timesale))

    def remove_timesale_options_handler(self, handler: callable):
        self.handlers["TIMESALE_OPTIONS"].remove(Handler(handler, Fields.timesale))

    # ------------------------------------------------------------------------------------------------------------------
    # TIMESALE_FUTURES
    async def timesale_futures_sub(self, symbols: str | list):
        """
        Subscribe to Level 2 Futures
        :param symbols: Future Symbol or list of symbols to Subscribe to
        :return: None
        """

        service = "TIMESALE_FUTURES"
        command = "SUBS"
        fields = 4

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"Futures TimeSale Subscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Futures TimeSale Subscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    async def timesale_futures_unsub(self, symbols: str | list):
        """
        Unsubscribe to Level 2 Futures
        :param symbols: Future Symbol or list of symbols to Unsubscribe to
        :return: None
        """

        service = "TIMESALE_FUTURES"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"Futures TimeSale Unsubscription SUCCESS."
                             f"Symbols: {symbols}. msg: {response.get('msg')}")
        else:
            self.logger.error(f"Futures TimeSale Unsubscription FAILED."
                              f"Symbols: {symbols}. Response: {response}")

    def add_timesale_futures_handler(self, handler: callable):
        self.handlers["TIMESALE_FUTURES"].append(Handler(handler, Fields.timesale))

    def remove_timesale_futures_handler(self, handler: callable):
        self.handlers["TIMESALE_FUTURES"].remove(Handler(handler, Fields.timesale))

    ####################################################################################################################

    # News
    # NEWS_HEADLINE
    async def news_headline_sub(self, symbols: str | list):
        """
        Subscribe to News Headlines
        :param symbols: Symbol or list of symbols to Subscribe to
        :return: None
        """

        service = "NEWS_HEADLINE"
        command = "SUBS"
        fields = 10

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command,
                                              fields=fields)

        if response.get("code") == 0:
            self.logger.info(f"News Headline Subscription SUCCESS. msg: {response.get('msg')}")
        else:
            self.logger.error(f"News Headline Subscription FAILED. Response: {response}")

    async def news_headline_unsub(self, symbols: str | list):
        """
        Unsubscribe from News Headlines
        :param symbols: Symbol or list of symbols to Unsubscribe from
        :return: None
        """

        service = "NEWS_HEADLINE"
        command = "UNSUBS"

        # Convert symbols to list if str
        if isinstance(symbols, str):
            symbols = [symbols]

        response = await self.service_request(symbols=symbols,
                                              service=service,
                                              command=command)

        if response.get("code") == 0:
            self.logger.info(f"News Headline Unsubscription SUCCESS. msg: {response.get('msg')}")
        else:
            self.logger.error(f"News Headline Unsubscription FAILED. Response: {response}")

    def add_news_headline_handler(self, handler: callable):
        self.handlers["NEWS_HEADLINE"].append(Handler(handler, Fields.news_headline))

    def remove_news_headline_handler(self, handler: callable):
        self.handlers["NEWS_HEADLINE"].remove(Handler(handler, Fields.news_headline))

    ####################################################################################################################
