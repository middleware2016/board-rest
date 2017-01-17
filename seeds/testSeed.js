/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let bcrypt = require('bcrypt-nodejs');

exports.seed = function(knex, Promise) {
    return Promise.join(
        // Deletes ALL existing entries
        knex('users').del(),

        //user
        new Promise(function(resolve, reject) {
            bcrypt.genSalt(10, function(err, salt) {
                bcrypt.hash('test', salt, null, function(err, hash) {
                    resolve(hash);
                });
            })
        }).then(function(hash){
            return knex('users').insert({id: 1, name: 'test', email:'test@test.com', password:hash, created_at: Date.now(), updated_at: Date.now()});
        })
    );
};