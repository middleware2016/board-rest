/**
 * Created by claudio on 23/02/17.
 */
"use strict";
let moment = require('moment');
let jwt = require('jsonwebtoken');
let dotenv = require('dotenv');
dotenv.load();

function generateToken(id) {
    var payload = {
        iss: process.env.DOMAIN,
        sub: id,
        iat: moment().subtract(7, 'days').unix(),
        exp: moment().unix()
    };
    return jwt.sign(payload, process.env.TOKEN_SECRET);
}

if(process.argv.length != 3){
    console.error('Usage node expired.js {ID}');
    process.exit();
}
console.log('Token',generateToken(process.argv[2]));