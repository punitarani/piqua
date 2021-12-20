import unittest
from lib.tda.auth.oauth import Authenticate


class RemoteAuthTest(unittest.TestCase):
    def test_Authenticate(self):
        data = Authenticate(override_mode="remote").token_header
        self.assertListEqual(list(data.keys()), ['Authorization'])
        self.assertEqual(data['Authorization'][0:6], 'Bearer')


if __name__ == '__main__':
    unittest.main()
