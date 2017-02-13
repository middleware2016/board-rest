/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let bcrypt = require('bcrypt-nodejs');
let bookshelf = require('../bookshelf');
bookshelf.plugin('registry');
let User = require('./User');
let Game = require('./Game');


let Play = bookshelf.Model.extend({
    tableName: 'plays',
    hasTimestamps: true, //manage in automatic way created_at and updated_at
    hidden: ['json_additional_data'], //hide from json deserialized
    user() {
        return this.belongsTo('User', 'user_id');
    },
    game() {
        return this.belongsTo('Game', 'game_id');
    },
    virtuals: {
        //serialize/deserialize additional data
        //mutators should be used, but I haven't found how to use them with bookshelf
        additional_data: {
            get () {
                try {
                    var data = this.get('json_additional_data');
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
                    this.set('json_additional_data', JSON.stringify(value));
                }catch (e)
                {
                    throw e;
                }
            }
        },

        links: function() {
            var links = {
                'self': '/users/' + this.get('user_id') + '/plays/' + this.get('id'),
                'user': '/users/' + this.get('user_id'),
                'game': '/games/' + this.get('game_id'),
            };
            for(let datum of this.get('additional_data')) {
                if('winner' in datum) {
                    links['winner'] = '/users/' + datum['winner'];
                    break;
                }
            }
            return links;
        }
    },
});

module.exports = bookshelf.model('Play', Play);
