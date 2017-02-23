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

    @classmethod
    def loginAs(cls, email, password):
        """Return the headers"""
        res = requests.post('{}/users/login'.format(BASE_URL), json = {'email': email, 'password': password})
        token = str(res.json()['token'])
        return {'Authorization':'Bearer '+token}

    @classmethod
    def setUpClass(cls):
        # Creating user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'initial', 'email': 'initial@middleware.polimi', 'password': '12345'})
        UserTest.initial_user_id = str(res.json()['id'])

        # Login with that user
        UserTest.headersObj = UserTest.loginAs('initial@middleware.polimi', '12345')

    @classmethod
    def tearDownClass(cls):
        UserTest.delete_all()

    @classmethod
    def delete_all(cls):
        # Deleting all existing users
        res = requests.delete('{}/clean'.format(BASE_URL))

    def test_user_creation(self):
        """Creates an user and checks that it exists."""
        # Creating user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'new1', 'email': 'new1@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        user_id = str(res.json()['id'])

        # Checking user
        res = requests.get('{}/users/{}'.format(BASE_URL, user_id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['name'], 'new1')

    def test_put_user_without_auth(self):
        """Tries to modify a user profile without login. Expected: 401"""
        # Doing a PUT without auth
        res = requests.put('{}/users/{}'.format(BASE_URL, UserTest.initial_user_id), json = {'name':'gfhfgh', 'email': 'fghfg@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 401)

    def test_put_own_user_with_auth(self):
        """Logged user tries to modify its own profile. Expected: 200"""
        # Doing a PUT with auth
        res = requests.put('{}/users/{}'.format(BASE_URL, UserTest.initial_user_id), json = {'name':'updated_initial', 'email': 'updated_initial@email.com', 'password': 'secret'}, headers = UserTest.headersObj)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['name'], 'updated_initial')
        self.assertEqual(res.json()['email'], 'updated_initial@email.com')

    def test_normal_put_other_user(self):
        """Logged unprivileged user tries to modify the profile of another user. Expected: 403"""
        # Create another user.
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'to_modify', 'email': 'to_modify@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        user_id = str(res.json()['id'])
        # Doing a PUT with auth
        res = requests.put('{}/users/{}'.format(BASE_URL, user_id), json = {'name':'dfssadf', 'email': 'new@email.com', 'password': '12345'}, headers = UserTest.headersObj)
        self.assertEqual(res.status_code, 403)

    def test_power_put_other_user(self):
        """Logged power user tries to modify the profile of another user. Expected: 403"""
        # Create another user.
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'to_modify2', 'email': 'to_modify2@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        user_id = str(res.json()['id'])
        # Login as power user
        powerHeaders = UserTest.loginAs('poweruser1@test.com', 'test')
        # Doing a PUT with auth
        res = requests.put('{}/users/{}'.format(BASE_URL, user_id), json = {'name':'dfssadf', 'email': 'new@email.com', 'password': '12345'}, headers = powerHeaders)
        self.assertEqual(res.status_code, 200)

    def test_delete_own_with_auth(self):
        """Logged user deletes his own profile. Expected: 200, then 404 on subsequent GET."""
        # Creating user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'to_delete', 'email': 'delete@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        user_id = str(res.json()['id'])
        uHeaders = self.loginAs('delete@middleware.polimi', '12345')
        # Deleting user with auth
        res = requests.delete('{}/users/{}'.format(BASE_URL, user_id), headers = uHeaders)
        self.assertEqual(res.status_code, 200)
        # Checking user
        res = requests.get('{}/users/{}'.format(BASE_URL, user_id))
        self.assertEqual(res.status_code, 404)

    def test_delete_without_auth(self):
        """Anonymous user tries to delete the profile. Expected: 401"""
        res = requests.delete('{}/users/{}'.format(BASE_URL, UserTest.initial_user_id))
        self.assertEqual(res.status_code, 401)

    def test_user_list(self):
        # Checking the list of users
        res = requests.get('{}/users'.format(BASE_URL))
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.json()), 1)
        numUsers = len(res.json())

        # Creating two users
        for i in range(2):
            res = requests.post('{}/users'.format(BASE_URL), json = {'name':'prova{}'.format(i), 'email': 'prova{}@middleware.polimi'.format(i), 'password': '12345'})
            self.assertEqual(res.status_code, 201)

        # Checking the list of users
        res = requests.get('{}/users'.format(BASE_URL))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), numUsers+2)

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
        os.system('npm run seeds')

        # Creating game without auth
        res = requests.post('{}/games'.format(BASE_URL), json = {'name':'Chess', 'designers': ['a', 'b'], 'cover': 'imagedata'})
        self.assertEqual(res.status_code, 401)

        # Login no power
        headersObj = UserTest.loginAs('testuser2@test.com', 'test')

		# Creating game with auth (no power)
        res = requests.post('{}/games'.format(BASE_URL), json = {'name':'Chess', 'designers': ['a', 'b'], 'cover': 'imagedata'}, headers=headersObj)
        self.assertEqual(res.status_code, 403)

        # Login power
        headersObj = UserTest.loginAs('poweruser1@test.com', 'test')

        # Creating game with auth (power)
        res = requests.post('{}/games'.format(BASE_URL), json = {'name':'Chess', 'designers': ['a', 'b'], 'cover': 'imagedata'}, headers=headersObj)
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
    headersObj = ''
    timestamp = int(datetime.datetime.now().strftime("%s"))

    @classmethod
    def setUpClass(cls):
        super(PlayTest, cls).setUpClass()

        os.system('npm run seeds')
        # Create a new user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'play_user', 'email': 'play_user@test.com', 'password': '12345'})
        PlayTest.user_id = res.json()['id']

        PlayTest.headersObj = UserTest.loginAs('play_user@test.com', '12345')

        # Get game 1
        res = requests.get('{}/games'.format(BASE_URL))
        PlayTest.game_id = res.json()[0]['id']

    def test_create_own_play(self):
        """Normal user tries to create a play of his user. Expected: 201"""
        # Create a new play
        res = requests.post('{}/users/{}/plays'.format(BASE_URL, PlayTest.user_id),
                            json = {
                                'name': 'play_user',
                                'additional_data': {'a': 'b'},
                                'played_at': PlayTest.timestamp,
                                'game_id': PlayTest.game_id}, headers=PlayTest.headersObj)
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

    def test_create_others_play_nopower(self):
        """Normal user tries to create a play of another user. Expected: 403"""
        # Create another user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'play_owner', 'email': 'play_owner@test.com', 'password': '12345'})
        owner_id = res.json()['id']
        # Create a new play for that user, with the credentials of the original user
        res = requests.post('{}/users/{}/plays'.format(BASE_URL, owner_id),
                            json = {
                                'name': 'Prova',
                                'additional_data': {'x': 'y'},
                                'played_at': PlayTest.timestamp,
                                'game_id': PlayTest.game_id}, headers=PlayTest.headersObj)
        self.assertEqual(res.status_code, 403)

    def test_create_others_play_power(self):
        """Power user tries to create a play of another user. Expected: 201"""
        # Create another user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'play_owner2', 'email': 'play_owner2@test.com', 'password': '12345'})
        owner_id = res.json()['id']
        # Login as power user
        powerHeaders = UserTest.loginAs('poweruser1@test.com', 'test')
        # Create a new play for that user, with the power user credentials
        res = requests.post('{}/users/{}/plays'.format(BASE_URL, owner_id),
                            json = {
                                'name': 'Prova',
                                'additional_data': {'x': 'y'},
                                'played_at': PlayTest.timestamp,
                                'game_id': PlayTest.game_id}, headers=powerHeaders)
        self.assertEqual(res.status_code, 201)

    def test_invalid_gameid(self):
        # Create a new play with invalid game id
        res = requests.post('{}/users/{}/plays'.format(BASE_URL, PlayTest.user_id),
                            json = {
                                'name': 'play_user',
                                'additional_data': {'a': 'b'},
                                'played_at': PlayTest.timestamp,
                                'game_id': -1}, headers=PlayTest.headersObj)
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

        res = requests.post('{}/users/login'.format(BASE_URL), json = {'email': 'poweruser1@test.com', 'password': 'test'})
        self.assertEqual(res.status_code, 200)
        token = str(res.json()['token'])
        PlayTest.headersObj = {'Authorization':'Bearer '+token}

        for i in range(num_plays):
            res = requests.post('{}/games'.format(BASE_URL), json = {'name':'G{}'.format(i), 'designers': ['a', 'b'], 'cover': 'imagedata'}, headers=PlayTest.headersObj)
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
        #self.assertEqual(len(res.json()), num_plays)
        for i in range(len(res.json())-1):
            self.assertGreater(res.json()[i]['game_id'], res.json()[i+1]['game_id'])

        # Get games for user, ordered by game id, ascending
        res = requests.get(
            '{}/users/{}/plays'.format(BASE_URL, u1_id),
            params={'order': 'game_id', 'order_type': 'asc'})
        self.assertEqual(res.status_code, 200)
        #self.assertEqual(len(res.json()), num_plays)
        for i in range(len(res.json())-1):
            self.assertLess(res.json()[i]['game_id'], res.json()[i+1]['game_id'])

if __name__ == '__main__':
    unittest.main()
