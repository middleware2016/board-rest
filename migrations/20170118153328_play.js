
exports.up = function(knex, Promise) {
    return Promise.all([
        knex.schema.createTable('plays', function(table) {
            table.increments();
            table.integer('user_id').unsigned().index().references('id').inTable('users').onDelete('cascade')
                .onUpdate('cascade');
            table.integer('game_id').unsigned().index().references('id').inTable('games').onDelete('cascade')
                .onUpdate('cascade');
            table.string('name');
            table.datetime('played_at');
            table.json('json_additional_data');
            table.timestamps();
        })
    ]);
};

exports.down = function(knex, Promise) {
    return Promise.all([
        knex.schema.dropTable('plays')
    ])
};
