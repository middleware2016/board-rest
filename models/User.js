/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let bcrypt = require('bcrypt-nodejs');
let bookshelf = require('../bookshelf');
bookshelf.plugin('registry');


let User = bookshelf.Model.extend({
    tableName: 'users',
    hasTimestamps: true, //manage in automatic way created_at and updated_at

    initialize: function() {
        this.on('saving', this.hashPassword, this);
    },

    hashPassword: function(model, attrs, options) {
        let password = options.patch ? attrs.password : model.get('password');
        if (!password) { return; }
        return new Promise(function(resolve, reject) {
            bcrypt.genSalt(10, function(err, salt) {
                bcrypt.hash(password, salt, null, function(err, hash) {
                    if (options.patch) {
                        attrs.password = hash;
                    }
                    model.set('password', hash);
                    resolve();
                });
            });
        });
    },

    comparePassword: function(password, done) {
        let model = this;
        bcrypt.compare(password, model.get('password'), function(err, isMatch) {
            done(err, isMatch);
        });
    },

    hidden: ['password'], //hide from json deserialized
});

module.exports = bookshelf.model('User', User);
