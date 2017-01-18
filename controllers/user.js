/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let User = require('../models/User');

exports.list = (req, res, next)=>{
    //order
    let order = req.query.order || 'created_at';
    let orderType = req.query.order_type;
    if(orderType!='desc')
        orderType = 'asc';

    //filters
    let search = req.query.search || '%';

    //retrieve
    return User.forge()
        .query(wb=>
            wb.where('name', 'LIKE', search)
            .orWhere('email', 'LIKE', search)
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
    return new User({id: req.params.id}).fetch()
        .then(data=>{
            if(!data)
                return res.status(404).send({msg: "User not found"});
            res.send(data.toJSON());
        })
        .catch(err=>{
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        })
};

exports.post = (req, res, next)=>{
    req.assert('name', 'Name cannot be blank').notEmpty();
    req.assert('email', 'Email is not valid').isEmail();
    req.assert('email', 'Email cannot be blank').notEmpty();
    req.assert('password', 'Password must be at least 4 characters long').len(4);
    req.sanitize('email').normalizeEmail({ remove_dots: false });

    var errors = req.validationErrors();

    if (errors) {
        return res.status(422).send(errors);
    }

    return new User({
        name: req.body.name,
        email: req.body.email,
        password: req.body.password
    }).save()
        .then(data=>res.send(data.toJSON()))
        .catch((err) => {
            if (err.code === 'ER_DUP_ENTRY' || err.code == '23505' || err.code == 'SQLITE_CONSTRAINT') {
                return res.status(422).send({ msg: 'The name/email you have entered is already associated with another account.' });
            }
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        });
};