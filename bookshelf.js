/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let config = require('./knexfile');
let knex = require('knex')(config);
let bookshelf = require('bookshelf')(knex);

bookshelf.plugin('virtuals');
bookshelf.plugin('visibility');

knex.migrate.latest();

module.exports = bookshelf;
//var bookshelf = require('../config/bookshelf');