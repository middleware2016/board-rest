/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let express = require('express');
let dotenv = require('dotenv');
let logger = require('morgan');
let moment = require('moment');//keep even if it is not used directly

//controllers
let user = require('./controllers/user');

dotenv.load();
let app = express();

app.set('port', process.env.PORT || 3000);
app.use(logger('dev'));

//routes
app.get('/', function (req, res) {
    res.send('Hello World!');
});
app.get('/users/', user.list);


app.listen(app.get('port'), function() {
    console.log('Express server listening on port ' + app.get('port'));
});