const request = require('supertest');
const assert = require('assert');
var config = require('../knexfile');
var knex = require('knex')(config);
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

    describe('Create and delete user', function() {
        it('Gets the list of users', function(done) {
            request(app)
            .post('/users')
            .send({ name: 'Prova', email: 'prova@gmail.com', password: 'lofggdfl' })
            .expect(201)
            .then(() => { return
                request(app)
                .get('/users/1')
                .set('Accept', 'application/json')
                .expect('Content-Type', /json/)
                .expect(200, function(res) {
                    res.body.name = 'Provaa';
                    console.log(res.body); // not working
                })
            })
            .then(() => { return
                request(app)
                .delete('/users/1')
                .expect(200)
            })
            .then(done);


        });
    });
});
