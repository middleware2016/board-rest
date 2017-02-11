const request = require('supertest');
const assert = require('assert');
// var config = require('../knexfile');
// var knex = require('knex')(config);
const app = require('../server.js');

describe('User', function() {
    // Knex conflicting on SQLite
    before(function(done) {
        // knex.migrate.rollback(config).then(function() {
        //     done();
        // });
        done();
    });

    beforeEach(function(done) {
        // knex.migrate.latest(config).then(function() {
        //     done();
        // });
        done();
    });

    afterEach(function(done) {
        // knex.migrate.rollback(config).then(function() {
        //     done();
        // });
        done();
    });

    describe('GET /users', function() {
        // Not working for some reason
        it('Gets the list of users', function(done) {
            request(app)
            .get('/users')
            .set('Accept', 'application/json')
            .expect('Content-Type', /html/)
            .expect(200, done);
        });
    });
});
