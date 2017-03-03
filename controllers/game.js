/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let Game = require('../models/Game');

exports.list = (req, res, next)=>{
    //order
    let order = req.query.order || 'created_at';
    let orderType = req.query.order_type;
    if(orderType!='desc')
        orderType = 'asc';

    //filters
    let search = req.query.search || '%';

    //retrieve
    return Game.forge()
        .query(wb=>
            wb.where('name', 'LIKE', search)
            .orWhere('json_designers', 'LIKE', search)
        )
        .orderBy(order, orderType)
        .fetchAll()
        .then(data=>res.send(data.toJSON()))
        .catch(err=>{
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        })
};

exports.get = (req, res, next)=>{
    return new Game({id: req.params.id}).fetch()
        .then(data=>{
            if(!data)
                return res.status(404).send({msg: "Game not found"});
            res.send(data.toJSON())
        })
        .catch(err=>{
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        })
};

exports.post = (req, res, next)=>{
    if (req.user.get('role') != 'power')
        return res.status(403).send({msg: "You are not a power user"});

    req.assert('name', 'Name cannot be blank').notEmpty();
    req.assert('designers', 'Designers cannot be blank').notEmpty(); //TODO check is list
    req.assert('cover', 'Cover cannot be blank').notEmpty();

    let errors = req.validationErrors();

    if (errors) {
        return res.status(422).send(errors);
    }

    return new Game({
        name: req.body.name,
        designers: req.body.designers,
        cover: req.body.cover
    }).save()
        .then(data=>res.status(201).send(data.toJSON()))
        .catch((err) => {
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        });
};
