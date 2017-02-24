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

def runSeeds():
    """Run seeds to reset the database"""
    with open(os.devnull, 'w') as devnull:
        subprocess.call(["npm", "run", "seeds"], stdout=devnull)

def get_options_verbs(url):
    """Performs an OPTIONS HTTP request on the given URL and gives the list of allowed HTTP verbs."""
    res = requests.options(url)
    verbs = res.headers['Allow'].split(',')
    return verbs

class RestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runSeeds()

class UserTest(RestTest):
    # Before and after the test suite, delete all the users.

    @classmethod
    def loginAs(cls, email, password):
        """Return the headers"""
        res = requests.post('{}/users/login'.format(BASE_URL), json = {'email': email, 'password': password})
        token = str(res.json()['token'])
        return {'Authorization':'Bearer '+token}

    @classmethod
    def getExpiredToken(cls, userId):
        """Calls the Node script to get an expired token for the given user ID."""
        return subprocess.check_output(["node", "expired.js", str(userId)], universal_newlines=True).strip()

    @classmethod
    def setUpClass(cls):
        """Creates a normal user for testing. This user should not be deleted by the tests."""
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
        """Delete all the existing users."""
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
        res = requests.put('{}/users/{}'.format(BASE_URL, user_id), json = {'name':'ppou', 'email': 'ppou@email.com', 'password': '12345'}, headers = powerHeaders)
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

    def test_power_delete(self):
        """A power user deletes another user. Expected: 200"""
        # Login as power user
        powerHeaders = UserTest.loginAs('poweruser1@test.com', 'test')
        # Create a normal user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'to_delete_from_power', 'email': 'to_delete_from_power@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        user_id = str(res.json()['id'])
        # Nuke!
        res = requests.delete('{}/users/{}'.format(BASE_URL, user_id), headers = powerHeaders)
        self.assertEqual(res.status_code, 200)

    def test_delete_without_auth(self):
        """Anonymous user tries to delete the profile. Expected: 401"""
        res = requests.delete('{}/users/{}'.format(BASE_URL, UserTest.initial_user_id))
        self.assertEqual(res.status_code, 401)

    def test_normal_privilege_escalation(self):
        """A normal user tries to become power user. Expected: 403"""
        res = requests.put('{}/users/{}'.format(BASE_URL, UserTest.initial_user_id), json = {'name':'updated_initial', 'email': 'updated_initial@email.com', 'password': 'secret', 'role': 'power'}, headers = UserTest.headersObj)
        self.assertEqual(res.status_code, 403)

    def test_power_promote_user(self):
        """A power user makes another user a power user. Expected: 200"""
        # Login as power user
        powerHeaders = UserTest.loginAs('poweruser1@test.com', 'test')
        # Create a normal user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'to_promote', 'email': 'to_promote@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        user_id = str(res.json()['id'])
        res = requests.put('{}/users/{}'.format(BASE_URL, user_id), json = {'name':'to_promote', 'email': 'to_promote@email.com', 'password': 'secret', 'role': 'power'}, headers = powerHeaders)
        self.assertEqual(res.status_code, 200)

    def test_user_list(self):
        """Checks on the length of the user list."""
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
        """Try to create an user with an invalid email. Expected: 401"""
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'invalid_email_user', 'email': 'invalid_email', 'password': '12345'})
        self.assertEqual(res.status_code, 422)

    def test_short_password(self):
        """Try to create an user with a password which is too short. Expected: 401"""
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'short_pass_user', 'email': 'short_pass_user@test.com', 'password': '123'})
        self.assertEqual(res.status_code, 422)

    def test_same_email(self):
        """Try to create two user with the same email. Expected: 201, 401"""
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'same_email1', 'email': 'same_email@test.com', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'same_email2', 'email': 'same_email@test.com', 'password': '12345'})
        self.assertEqual(res.status_code, 422)

    def test_same_name(self):
        """Try to create two user with the same name. Expected: 201, 401"""
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'same_name', 'email': 'same_name1@test.com', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'same_name', 'email': 'same_name2@test.com', 'password': '12345'})
        self.assertEqual(res.status_code, 422)

    def test_get_non_existing_user(self):
        """Try to GET a nonexisting user. Expected: 404"""
        res = requests.get('{}/users/-1'.format(BASE_URL))
        self.assertEqual(res.status_code, 404)

    def test_options_user_list(self):
        """OPTIONS on /users should return GET, POST"""
        verbs = get_options_verbs('{}/users'.format(BASE_URL))
        self.assertEqual(len(verbs), 2)
        self.assertTrue('GET' in verbs)
        self.assertTrue('POST' in verbs)

    def test_options_user(self):
        """OPTIONS on /users/:id should return GET, PUT, DELETE"""
        verbs = get_options_verbs('{}/users/{}'.format(BASE_URL, UserTest.initial_user_id))
        self.assertEqual(len(verbs), 3)
        self.assertTrue('GET' in verbs)
        self.assertTrue('PUT' in verbs)
        self.assertTrue('DELETE' in verbs)

    def test_zombie_token(self):
        """A token of a deleted user is used to attempt a privileged action. Expected: 401"""
        # Create a new user
        res = requests.post('{}/users'.format(BASE_URL), json = {'name':'zombie', 'email': 'zombie@middleware.polimi', 'password': '12345'})
        self.assertEqual(res.status_code, 201)
        user_id = str(res.json()['id'])
        uHeaders = self.loginAs('zombie@middleware.polimi', '12345')

        # Login as power user, delete zombie
        powerHeaders = UserTest.loginAs('poweruser1@test.com', 'test')
        res = requests.delete('{}/users/{}'.format(BASE_URL, user_id), headers = powerHeaders)
        self.assertEqual(res.status_code, 200)

        # Try to change profile with zombie's headers. Rejected!
        res = requests.put('{}/users/{}'.format(BASE_URL, user_id), json = {'name':'zombie2', 'email': 'zombie2@email.com', 'password': 'secret'}, headers = uHeaders)
        self.assertEqual(res.status_code, 401)

    def test_expired_token_login(self):
        """An expired token is used to attempt an action from a logged in user. Expected: 401"""
        expiredToken = self.getExpiredToken(UserTest.initial_user_id)
        expiredHeader = {'Authorization' : 'Bearer ' + expiredToken}
        # Attempt to change profile
        res = requests.put('{}/users/{}'.format(BASE_URL, UserTest.initial_user_id), json = {'name':'expired', 'email': 'expired@email.com', 'password': 'secret'}, headers = expiredHeader)
        self.assertEqual(res.status_code, 401)

    def test_invalid_token_login(self):
        """An altered token is used to attempt an action from a logged in user. Expected: 401"""
        newHeader = {'Authorization' : 'Bearer ' + UserTest.headersObj['Authorization'] + 'x'}
        # Attempt to change profile
        res = requests.put('{}/users/{}'.format(BASE_URL, UserTest.initial_user_id), json = {'name':'expired', 'email': 'expired@email.com', 'password': 'secret'}, headers = newHeader)
        self.assertEqual(res.status_code, 401)


class GameTest(RestTest):
    def test_anon_create_game(self):
        """Create a game without auth. Expected: 401"""
        res = requests.post('{}/games'.format(BASE_URL), json = {'name':'Chess', 'designers': ['a', 'b'], 'cover': 'imagedata'})
        self.assertEqual(res.status_code, 401)

    def test_normal_create_game(self):
        """Normal user tries to create game. Expected: 401"""
        # Login no power
        headersObj = UserTest.loginAs('testuser2@test.com', 'test')

		# Creating game with auth (no power)
        res = requests.post('{}/games'.format(BASE_URL), json = {'name':'Chess', 'designers': ['a', 'b'], 'cover': 'imagedata'}, headers=headersObj)
        self.assertEqual(res.status_code, 403)

    def test_power_create_game(self):
        """Power user tries to create game. Expected: 201"""
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

    def test_delete_game(self):
        """Anonymous user tries to delete a game. Expected: 405"""
        # Get list of games
        res = requests.get('{}/games'.format(BASE_URL))
        game_id = res.json()[0]['id']
        # Deleting game: not supported
        res = requests.delete('{}/games/{}'.format(BASE_URL, game_id))
        self.assertEqual(res.status_code, 405)

    def test_get_list_games(self):
        """Gets the list of games. Expected: 200, at least one game"""
        res = requests.get('{}/games'.format(BASE_URL))
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.json()), 1)

    def test_game_list_options(self):
        """OPTIONS on /games should return GET, POST"""
        verbs = get_options_verbs('{}/games'.format(BASE_URL))
        self.assertEqual(len(verbs), 2)
        self.assertTrue('GET' in verbs)
        self.assertTrue('POST' in verbs)

    def test_game_options(self):
        """OPTIONS on /games/:id should return GET"""
        verbs = get_options_verbs('{}/games/1'.format(BASE_URL))
        self.assertEqual(len(verbs), 1)
        self.assertTrue('GET' in verbs)

class PlayTest(RestTest):

    user_id = None
    game_id = None
    headersObj = ''
    timestamp = int(datetime.datetime.now().strftime("%s"))

    @classmethod
    def setUpClass(cls):
        super(PlayTest, cls).setUpClass()
        runSeeds()

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
        """Create a new play with invalid game id. Expected: 422"""
        res = requests.post('{}/users/{}/plays'.format(BASE_URL, PlayTest.user_id),
                            json = {
                                'name': 'play_user',
                                'additional_data': {'a': 'b'},
                                'played_at': PlayTest.timestamp,
                                'game_id': -1}, headers=PlayTest.headersObj)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(res.json()[0]['param'], 'game_id')

    def test_get_non_existing_play(self):
        """Try to get a nonexisting play on an existing user. Expected: 404"""
        res = requests.get('{}/users/{}/plays/-1'.format(BASE_URL, PlayTest.user_id))
        self.assertEqual(res.status_code, 404)

    def test_search_plays_by_gameid(self):
        """Tests on the search of plays for a specific user, ordered by game id."""
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

        # Get plays for user, ordered by game id, descending
        res = requests.get(
            '{}/users/{}/plays'.format(BASE_URL, u1_id),
            params={'order': 'game_id', 'order_type': 'desc'})
        self.assertEqual(res.status_code, 200)
        #self.assertEqual(len(res.json()), num_plays)
        for i in range(len(res.json())-1):
            self.assertGreater(res.json()[i]['game_id'], res.json()[i+1]['game_id'])

        # Get plays for user, ordered by game id, ascending
        res = requests.get(
            '{}/users/{}/plays'.format(BASE_URL, u1_id),
            params={'order': 'game_id', 'order_type': 'asc'})
        self.assertEqual(res.status_code, 200)
        #self.assertEqual(len(res.json()), num_plays)
        for i in range(len(res.json())-1):
            self.assertLess(res.json()[i]['game_id'], res.json()[i+1]['game_id'])

    def test_plays_list_options(self):
        """OPTIONS on /users/:id/plays should return GET, POST"""
        verbs = get_options_verbs('{}/users/{}/plays'.format(BASE_URL, PlayTest.user_id))
        self.assertEqual(len(verbs), 2)
        self.assertTrue('GET' in verbs)
        self.assertTrue('POST' in verbs)

    def test_plays_options(self):
        """OPTIONS on /users/:id/plays/:pid should return GET"""
        # Create a new play
        res = requests.post('{}/users/{}/plays'.format(BASE_URL, PlayTest.user_id),
                            json = {
                                'name': 'PlayOptions',
                                'additional_data': {'a': 'b'},
                                'played_at': PlayTest.timestamp,
                                'game_id': PlayTest.game_id}, headers=PlayTest.headersObj)
        play_id = res.json()['id']
        verbs = get_options_verbs('{}/users/{}/plays/{}'.format(BASE_URL, PlayTest.user_id, play_id))
        self.assertEqual(len(verbs), 1)
        self.assertTrue('GET' in verbs)

if __name__ == '__main__':
    unittest.main()
