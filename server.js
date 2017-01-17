/**
 * Created by claudio on 17/01/17.
 */

var express = require('express');
var dotenv = require('dotenv');

dotenv.load();
var app = express();

app.set('port', process.env.PORT || 3000);

app.get('/', function (req, res) {
    res.send('Hello World!');
});

app.listen(app.get('port'), function() {
    console.log('Express server listening on port ' + app.get('port'));
});