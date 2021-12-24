# TDA Stream Client

import asyncio
import json
from datetime import datetime
from urllib.parse import urlencode

import websockets
from websockets.extensions.permessage_deflate import ClientPerMessageDeflateFactory

from config import account_id
from ..account import Account
from ..logger import TDALogger

# Connected Webclient Sockets
client_socket = {}


class StreamClient:
    def __init__(self):
        """
        Initialize Stream Client
        :param login: Connect and Login to server when initialized
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

        self._ssl_context = 'ssl_context'

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

    async def service_request(self,
                              service: str,
                              command: str,
                              symbols: list,
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
