import requests
import unittest
import subprocess

BASE_URL = 'http://localhost:3000'

class UserTest(unittest.TestCase):
    def setUpClass():
        # Reset database
        subprocess.call(["npm", "run", "seeds"])

    def test_user_life(self):
        # Creating user
        res = requests.post(BASE_URL + '/users', json = {'name':'pietro', 'email': 'pietro@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        user_id = str(res.json()['id'])

        # Checking user
        res = requests.get(BASE_URL + '/users/' + user_id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['name'], 'pietro')

        # Doing a PUT
        res = requests.put(BASE_URL + '/users/' + user_id, json = {'name':'pietro', 'email': 'new@email.com', 'password': '12345'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['email'], 'new@email.com')

        # Deleting user
        res = requests.delete(BASE_URL + '/users/' + user_id)
        self.assertEqual(res.status_code, 200)

    def test_invalid_email(self):
        res = requests.post(BASE_URL + '/users', json = {'name':'pietro', 'email': 'sadfasdfas', 'password': '12345'})
        self.assertEqual(res.status_code, 422)

    def test_short_password(self):
        res = requests.post(BASE_URL + '/users', json = {'name':'pietro', 'email': 'abc@gmail.com', 'password': '123'})
        self.assertEqual(res.status_code, 422)


if __name__ == '__main__':
    unittest.main()
