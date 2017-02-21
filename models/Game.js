/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let bcrypt = require('bcrypt-nodejs');
let bookshelf = require('../bookshelf');
bookshelf.plugin('registry');


let Game = bookshelf.Model.extend({
    tableName: 'games',
    hasTimestamps: true, //manage in automatic way created_at and updated_at
    hidden: ['json_designers'], //hide from json deserialized

    plays() {
        return this.hasMany('Play', 'game_id');
    },

    virtuals: {
        //serialize/deserialize designers
        //mutators should be used, but I haven't found how to use them with bookshelf
        designers: {
            get () {
                try {
                    var data = this.get('json_designers');
                    try {
                        return JSON.parse(data);
                    }catch(e){
                        return data;
                    }
                }catch(e2){
                    throw e2;
                }
            },
            set: function(value) {
                try {
                    this.set('json_designers', JSON.stringify(value));
                }catch (e)
                {
                    throw e;
                }
            }
        },

        links: function() {
            return {
                'self': '/games/' + this.get('id'),
            };
        }
    },

});

module.exports = bookshelf.model('Game', Game);
