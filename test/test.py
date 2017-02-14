#!/usr/bin/env python3

"""
How to run the tests:
    cd test
    python -m unittest test

Requirements:
    * Python 2 or 3
    * Requests: http://docs.python-requests.org/en/master/
"""

import requests
import unittest
import subprocess
import datetime
import os

BASE_URL = 'http://localhost:3000'

class RestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reset database
        with open(os.devnull, 'w') as devnull:
            subprocess.call(["npm", "run", "seeds"], stdout=devnull)

class UserTest(RestTest):
    # Before and after each test, delete all the users.

    def setUp(self):
        self.delete_all_users()

    def tearDown(self):
        self.delete_all_users()

    def delete_all_users(self):
        # Deleting all existing users
        res = requests.get('{}/users'.format(BASE_URL))
        self.assertEqual(res.status_code, 200)
        for user in res.json():
            res = requests.delete('{}/users/{}'.format(BASE_URL, user['id']))
            self.assertEqual(res.status_code, 200)

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

    def test_user_list(self):
        # Checking the list of users
        res = requests.get('{}/users'.format(BASE_URL))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 0)

        # Creating two users
        for i in range(2):
            res = requests.post('{}/users'.format(BASE_URL), json = {'name':'prova{}'.format(i), 'email': 'prova{}@middleware.polimi'.format(i), 'password': '12345'})
            self.assertEqual(res.status_code, 201)

        # Checking the list of users
        res = requests.get('{}/users'.format(BASE_URL))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 2)

    def test_invalid_email(self):
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'invalid_email_user', 'email': 'invalid_email', 'password': '12345'})
        self.assertEqual(res.status_code, 422)

    def test_short_password(self):
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'short_pass_user', 'email': 'short_pass_user@test.com', 'password': '123'})
        self.assertEqual(res.status_code, 422)

    def test_same_email(self):
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'same_email1', 'email': 'same_email@test.com', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'same_email2', 'email': 'same_email@test.com', 'password': '12345'})
        self.assertEqual(res.status_code, 422)

    def test_same_name(self):
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'same_name', 'email': 'same_name1@test.com', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'same_name', 'email': 'same_name2@test.com', 'password': '12345'})
        self.assertEqual(res.status_code, 422)

    def test_get_non_existing_user(self):
        res = requests.get('{}/users/-1'.format(BASE_URL))
        self.assertEqual(res.status_code, 404)



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

    user_id = None
    game_id = None
    timestamp = int(datetime.datetime.now().strftime("%s"))

    @classmethod
    def setUpClass(cls):
        super(PlayTest, cls).setUpClass()

        # Create a new user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'play_user', 'email': 'play_user@test.com', 'password': '12345'})
        PlayTest.user_id = res.json()['id']

        # Create new game
        res = requests.post('{}/games'.format(BASE_URL), json = {'name':'Game1', 'designers': ['x', 'y'], 'cover': 'imagedata'})
        PlayTest.game_id = res.json()['id']

    def test_play_creation(self):
        # Create a new play
        res = requests.post('{}/users/{}/plays'.format(BASE_URL, PlayTest.user_id),
                            json = {
                                'name': 'play_user',
                                'additional_data': {'a': 'b'},
                                'played_at': PlayTest.timestamp,
                                'game_id': PlayTest.game_id})
        self.assertEqual(res.status_code, 201)

        # Check list of plays
        res = requests.get('{}/users/{}/plays'.format(BASE_URL, PlayTest.user_id))
        self.assertEqual(res.status_code, 200)
        # Should only return one play, for the current user
        self.assertEqual(len(res.json()), 1)
        play_id = str(res.json()[0]['id'])

        # Check the play, accessed directly
        res = requests.get('{}/users/{}/plays/{}'.format(BASE_URL, PlayTest.user_id, play_id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['additional_data'], {'a': 'b'})
        self.assertEqual(res.json()['played_at'], PlayTest.timestamp)
        self.assertEqual(res.json()['name'], 'play_user')
        self.assertEqual(res.json()['game_id'], PlayTest.game_id)

    def test_invalid_gameid(self):
        # Create a new play with invalid game id
        res = requests.post('{}/users/{}/plays'.format(BASE_URL, PlayTest.user_id),
                            json = {
                                'name': 'play_user',
                                'additional_data': {'a': 'b'},
                                'played_at': PlayTest.timestamp,
                                'game_id': -1})
        self.assertEqual(res.status_code, 422)
        self.assertEqual(res.json()[0]['param'], 'game_id')

    def test_get_non_existing_play(self):
        res = requests.get('{}/users/{}/plays/-1'.format(BASE_URL, PlayTest.user_id))
        self.assertEqual(res.status_code, 404)

    def test_search_plays_by_gameid(self):
        # Create a new user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'u1', 'email': 'u1@test.com', 'password': '12345'})
        u1_id = res.json()['id']

        # Create games and plays
        num_plays = 4
        game_ids = []
        for i in range(num_plays):
            res = requests.post('{}/games'.format(BASE_URL), json = {'name':'G{}'.format(i), 'designers': ['a', 'b'], 'cover': 'imagedata'})
            game_ids.append(res.json()['id'])

            # Create a play for each game
            res = requests.post('{}/users/{}/plays'.format(BASE_URL, u1_id),
                                json = {
                                    'name': 'Play{}'.format(i),
                                    'additional_data': {'a': 'b'},
                                    'played_at': PlayTest.timestamp + i * 10,
                                    'game_id': game_ids[i]})

        # Get games for user, ordered by game id, descending
        res = requests.get(
            '{}/users/{}/plays'.format(BASE_URL, u1_id),
            params={'order': 'game_id', 'order_type': 'desc'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), num_plays)
        for i in range(len(res.json())-1):
            self.assertGreater(res.json()[i]['game_id'], res.json()[i+1]['game_id'])

        # Get games for user, ordered by game id, ascending
        res = requests.get(
            '{}/users/{}/plays'.format(BASE_URL, u1_id),
            params={'order': 'game_id', 'order_type': 'asc'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), num_plays)
        for i in range(len(res.json())-1):
            self.assertLess(res.json()[i]['game_id'], res.json()[i+1]['game_id'])

if __name__ == '__main__':
    unittest.main()
