/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let User = require('../models/User');
let Game = require('../models/Game');
let Play = require('../models/Play');

exports.userMiddleware = (req, res, next) => {
    return new User({id: req.params.userId}).fetch().then((user)=>{
        req.user = user;
        next();
    }).catch(()=>{
        res.status(404).send({ msg: 'Wrong user id' });
    });
};


exports.list = (req, res, next)=>{
    //order
    let order = req.query.order || 'created_at';
    let orderType = req.query.order_type;
    if(orderType!='desc')
        orderType = 'asc';

    //filters
    let search = req.query.search || '%';

    //retrieve
    return req.user.related('plays')
        .query(wb=>
            wb.where('name', 'LIKE', search)
            .orWhere('additional_data', 'LIKE', search)
        )
        .orderBy(order, orderType)
        .fetch()
        .then(data=>res.send(data.toJSON()))
        .catch(err=>{
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        })
};

exports.get = (req, res, next)=>{
    return new Play({id: req.params.id}).fetch()
        .then(data=>{
            if(!data)
                return res.status(404).send({msg: "Play not found"});
            if(data.get('user_id') != req.user.id)
                return res.status(403).send({msg: "Play is not of this user"});
            res.send(data.toJSON())
        })
        .catch(err=>{
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        })
};

exports.post = (req, res, next)=>{
    req.assert('name', 'Name cannot be blank').notEmpty();
    req.assert('additional_data', 'Additional_data cannot be blank').notEmpty(); //TODO check is list/object
    req.assert('played_at', 'Played_at cannot be blank').isInt();
    req.assert('game_id', 'Game_id must be an integer').isInt();

    var errors = req.validationErrors();

    if (errors) {
        return res.status(422).send(errors);
    }

    return new Game({id: req.body.game_id}).fetch()
        .then(data=>{
            if(!data)
                return res.status(422).send([
                    {
                        "param": "game_id",
                        "msg": "Game_id inserted doesn't exist"
                    }
                ]);
            return req.user.plays().create({
                name: req.body.name,
                additional_data: req.body.additional_data,
                played_at: req.body.played_at,
                game_id: req.body.game_id,
            }).then(data=>res.send(data.toJSON()));
        })
        .catch(err=>{
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        });
};