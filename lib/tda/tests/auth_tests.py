import unittest

from lib.tda import authenticate, get_token, get_content


class AuthTest(unittest.TestCase):
    def test_authenticate(self):
        data = authenticate()
        self.assertListEqual(list(data.keys()), ['Authorization'])
        self.assertEqual(data['Authorization'][0:6], 'Bearer')

    def test_getToken(self):
        data = get_token()
        self.assertListEqual(list(data.keys()), ['Authorization'])
        self.assertEqual(data['Authorization'][0:6], 'Bearer')

    def test_getContent(self):
        data = get_content(url=r'https://api.tdameritrade.com/v1/userprincipals', headers=get_token())
        self.assertEqual(data.status_code, 200)


# Run All Tests
if __name__ == '__main__':
    unittest.main()
