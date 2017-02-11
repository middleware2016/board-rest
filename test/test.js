const request = require('supertest');
const assert = require('assert');
var config = require('../knexfile');
var knex = require('knex')(config);
const app = require('../server.js');
var requestInstance =  request(app);

describe('User', function() {
    // Knex conflicting on SQLite
    before(function(done) {
        // knex.migrate.rollback(config).then(function() {
        //     done();
        // });
        done();
    });

    beforeEach(function(done) {
/*         knex.migrate.latest(config).then(function() {
             done();
        });*/
        done();
    });

    afterEach(function(done) {
        // knex.migrate.rollback(config).then(function() {
        //     done();
        // });
        done();
    });

    describe('Create and delete user', function() {
        it('Gets the list of users', function() {
            var t =  requestInstance
            .post('/users')
            .send({ name: 'Prova', email: 'prova@gmail.com', password: 'lofggdfl' })
            .expect(201);
            return new Promise((resolve, reject)=>t.then(resolve).catch(reject))
            .then((data) => {
                var t = requestInstance
                .get('/users/1')
                .set('Accept', 'application/json')
                .expect('Content-Type', /json/)
                .expect(200,{
                    id: 'some fixed id',
                    name: 'TOBI'
                });
                return new Promise((resolve, reject)=>t.then(resolve).catch(reject));
            })
            .then((data) => {
                var t =
                requestInstance
                .delete('/users/1')
                .expect(200);
                return new Promise((resolve, reject)=>t.then(resolve).catch(reject));
            });

        });
    });
});
