
exports.up = function(knex, Promise) {
    return Promise.all([
        knex.schema.createTable('games', function(table) {
            table.increments();
            table.string('name');
            table.text('json_designers');
            table.text('cover'); //this is stored in base64
            table.timestamps();
        })
    ]);
};

exports.down = function(knex, Promise) {
    return Promise.all([
        knex.schema.dropTable('games')
    ])
};
