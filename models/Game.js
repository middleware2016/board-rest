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
    virtuals: {
        //serialize/deserialize designers
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
        }
    },
});

module.exports = bookshelf.model('Game', Game);
