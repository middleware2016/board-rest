/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let express = require('express');
let dotenv = require('dotenv');
let logger = require('morgan');
let moment = require('moment');//keep even if it is not used directly
var compression = require('compression');
var bodyParser = require('body-parser');
var expressValidator = require('express-validator');
var jwt = require('jsonwebtoken');
let User = require('./models/User');
let config = require('./knexfile');
let knex = require('knex')(config);

//controllers
let user = require('./controllers/user');
let game = require('./controllers/game');
let play = require('./controllers/play');

dotenv.load();
let app = express();

//config defaults
//post body limit
let requestLimit = process.env.REQUEST_LIMIT || 1024*1024*50; //50MB limit

//authentication
app.use((req, res, next) => {
    req.isAuthenticated = () => {
        let token = (req.headers.authorization && req.headers.authorization.split(' ')[1]);// || req.cookies.token;
        try {
            return jwt.verify(token, process.env.TOKEN_SECRET);
        } catch (err) {
            return false;
        }
    };

    if (req.isAuthenticated()) {
        let payload = req.isAuthenticated();
        new User({ id: payload.sub })
            .fetch()
            .then(function(user) {
                req.user = user;
                next();
            });
    } else {
        next();
    }
});
let ensureAuthenticated = (req, res, next) => {
    if (req.isAuthenticated() && req.user) {
        next();
    } else {
        res.status(401).send({ msg: 'Unauthorized' });
    }
};

app.set('port', process.env.PORT || 3000);
app.use(logger('dev'));
app.use(bodyParser.json({limit:requestLimit, type:'application/json'}));
app.use(bodyParser.urlencoded({ extended:true,limit:requestLimit,type:'application/x-www-form-urlencoding' }));
app.use(expressValidator());
app.use(compression());//gzip compression

//routes
/*app.get('/', function (req, res) {
    res.send('Hello World!');
});*/
//user
app.get('/users/', user.list);
app.get('/users/:id', user.get);
app.post('/users/', user.post);
app.put('/users/:id', ensureAuthenticated, user.put);
app.delete('/users/:id', ensureAuthenticated, user.delete);
app.post('/users/login', user.login);
app.options('/users/',(req,res)=>res.set('Allow', 'GET,POST').status(200).send());
app.options('/users/login',(req,res)=>res.set('Allow', 'POST').status(200).send()); //this must be before :id version
app.options('/users/:id',(req,res)=>res.set('Allow', 'GET,PUT,DELETE').status(200).send());

//games
app.get('/games/', game.list);
app.get('/games/:id', game.get);
app.post('/games/', ensureAuthenticated, game.post);
app.options('/games/',(req,res)=>res.set('Allow', 'GET,POST').status(200).send());
app.options('/games/:id',(req,res)=>res.set('Allow', 'GET').status(200).send());

//plays
app.get('/users/:userId/plays/', play.userMiddleware, play.list);
app.get('/users/:userId/plays/:id', play.userMiddleware, play.get);
app.post('/users/:userId/plays/', ensureAuthenticated, play.userMiddleware, play.post);
app.options('/users/:userId/plays/',(req,res)=>res.set('Allow', 'GET,POST').status(200).send());
app.options('/users/:userId/plays/:id',(req,res)=>res.set('Allow', 'GET').status(200).send());

//needed just for tests
app.delete('/clean', (req, res, next)=>{
    Promise.all([
        knex('users').del(),
        knex('games').del(),
        knex('plays').del()
    ]).then(()=>res.send('OK'));
});

//errors
let notImplemented = (req, res, next) =>{
    res.status(405).send(`Cannot ${req.method} ${req.url}`);
};

app.get('*', notImplemented);
app.post('*', notImplemented);
app.put('*', notImplemented);
app.delete('*', notImplemented);
app.options('*', (req,res)=>res.set('Allow', '').status(200).send());


app.listen(app.get('port'), function() {
    console.log('Express server listening on port ' + app.get('port'));
});

module.exports = app;
