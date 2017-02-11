/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let bcrypt = require('bcrypt-nodejs');

exports.seed = function(knex, Promise) {
    return Promise.join(
        // Deletes ALL existing entries
        knex('users').del(),
        knex('games').del(),
        knex('plays').del(),

        //user
        new Promise(function(resolve, reject) {
            bcrypt.genSalt(10, function(err, salt) {
                bcrypt.hash('test', salt, null, function(err, hash) {
                    resolve(hash);
                });
            })
        }).then(function(hash){
            return knex('users').insert({id: 1, name: 'test', email:'test@test.com', password:hash, created_at: Date.now(), updated_at: Date.now()});
        }),

        //games
        //TODO insert a base64 sample
        knex('games').insert({id: 1, name: 'test', json_designers: JSON.stringify(['test1', 'test2']), cover:'aaa', created_at: Date.now(), updated_at: Date.now()}),

        //playesames
        //TODO insert a base64 sample
        knex('plays').insert({id: 1, name: 'test', user_id:1, game_id: 1, json_additional_data: JSON.stringify([{winner: 1}]), played_at: Date.now(), created_at: Date.now(), updated_at: Date.now()})
    );
};