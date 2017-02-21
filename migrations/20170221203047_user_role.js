
exports.up = function(knex, Promise) {
    return Promise.all([
        knex.schema.table('users', function (table) {
            table.enu('role', ['normal', 'power']).default('normal')
        })
    ])
};

exports.down = function(knex, Promise) {
    return Promise.all([
        knex.schema.table('users', function (table) {
            table.dropColumn('role');
        })
    ])
};
