"use strict";
exports.up = function(knex, Promise) {
    return Promise.all([
        knex.schema.createTable('users', function(table) {
            table.increments();
            table.string('name').unique();
            table.string('email');
            table.string('password');
            table.timestamps();
        })
    ]);
};

exports.down = function(knex, Promise) {
    return Promise.all([
        knex.schema.dropTable('users')
    ])
};
