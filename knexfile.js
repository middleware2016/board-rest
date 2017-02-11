/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let dotenv = require('dotenv');
let pg = require('pg');

dotenv.load();


pg.defaults.ssl = true;
if(process.env.DATABASE_URL){
    module.exports = {
        client: 'mysql',
        connection: process.env.DATABASE_URL
    };
}else {
    module.exports = {
        client: 'sqlite',
        connection: {
            filename: './dev.sqlite3'
        },
        useNullAsDefault: true
    };
}
