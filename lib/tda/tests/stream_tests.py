import unittest
from ..streamclient import StreamClient
from unittest import IsolatedAsyncioTestCase


class TestStreamer(IsolatedAsyncioTestCase):
    async def test_stream_connect_disconnect(self):
        socket = StreamClient()
        await socket.login()

        run = True
        while run:
            disconnected = await socket.handle_socket_disconnect()
            if disconnected:
                run = False


if __name__ == '__main__':
    unittest.main()
