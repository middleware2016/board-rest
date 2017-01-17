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

//controllers
let user = require('./controllers/user');

dotenv.load();
let app = express();

//config defaults
//post body limit
let requestLimit = process.env.REQUEST_LIMIT || 1024*1024*50; //50MB limit

app.set('port', process.env.PORT || 3000);
app.use(logger('dev'));
app.use(bodyParser.json({limit:requestLimit, type:'application/json'}));
app.use(bodyParser.urlencoded({ extended:true,limit:requestLimit,type:'application/x-www-form-urlencoding' }));
app.use(expressValidator());
app.use(compression());//gzip compression

//routes
app.get('/', function (req, res) {
    res.send('Hello World!');
});
app.get('/users/', user.list);
app.get('/users/:id', user.get);
app.post('/users/', user.post);


app.listen(app.get('port'), function() {
    console.log('Express server listening on port ' + app.get('port'));
});