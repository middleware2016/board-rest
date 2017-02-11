#!/usr/bin/env python3

import requests
import unittest
import subprocess

BASE_URL = 'http://localhost:3000'

class RestTest(unittest.TestCase):
    def setUpClass():
        # Reset database
        subprocess.call(["npm", "run", "seeds"], stdout=subprocess.DEVNULL)

class UserTest(RestTest):
    def test_user_life(self):
        # Creating user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'pietro', 'email': 'pietro@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        user_id = str(res.json()['id'])

        # Checking user
        res = requests.get('{}/users/{}'.format(BASE_URL, user_id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['name'], 'pietro')

        # Doing a PUT
        res = requests.put('{}/users/{}'.format(BASE_URL, user_id), json = {'name':'pietro', 'email': 'new@email.com', 'password': '12345'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['email'], 'new@email.com')

        # Deleting user
        res = requests.delete('{}/users/{}'.format(BASE_URL, user_id))
        self.assertEqual(res.status_code, 200)

        # Checking user
        res = requests.get('{}/users/{}'.format(BASE_URL, user_id))
        self.assertEqual(res.status_code, 404)

    def test_invalid_email(self):
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'pietro', 'email': 'sadfasdfas', 'password': '12345'})
        self.assertEqual(res.status_code, 422)

    def test_short_password(self):
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'pietro', 'email': 'abc@gmail.com', 'password': '123'})
        self.assertEqual(res.status_code, 422)

class GameTest(RestTest):
    def test_game_creation(self):
        # Creating game
        res = requests.post('{}/games'.format(BASE_URL), json = {'name':'Chess', 'designers': ['a', 'b'], 'cover': 'imagedata'})
        self.assertEqual(res.status_code, 201)
        game_id = str(res.json()['id'])

        # Checking game existence
        res = requests.get('{}/games/{}'.format(BASE_URL, game_id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['name'], 'Chess')
        self.assertEqual(res.json()['designers'], ['a', 'b'])

        # Deleting game: not supported
        res = requests.delete('{}/games/{}'.format(BASE_URL, game_id))
        self.assertEqual(res.status_code, 405)

class PlayTest(RestTest):
    pass

if __name__ == '__main__':
    unittest.main()
