# board-rest
A service that can help people keep track of their board games nights, with a REST API.

## How to install
`npm install`

### Clean db and create fake data
`npm run seeds`

## How to run
`npm start`

## Tests
The tests require Python 2 or 3 and the `requests` library.

* To install requests: `pip install requests`
* To run the tests: `python test/test.py --verbose`

## Utils
### To create migrations
1. Install knex globally: `npm install -g knex`
2. Type `knex migrate:make NAME`
### To send auth token
Set header "Authorization" = "Bearer + JWTTOKEN"  
A secret key can be generated by secret.js and set as env var
### To store env vars
To store and load automatically env vars like `TOKEN_SECRET` put them into `.env` file as shwon in `.env.example` 