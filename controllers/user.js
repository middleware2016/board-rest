/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let User = require('../models/User');
let moment = require('moment');
var jwt = require('jsonwebtoken');

function generateToken(user) {
    var payload = {
        iss: process.env.DOMAIN,
        sub: user.id,
        iat: moment().unix(),
        exp: moment().add(7, 'days').unix()
    };
    return jwt.sign(payload, process.env.TOKEN_SECRET);
}

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
        .then(data=>res.status(201).send(data.toJSON()))
        .catch((err) => {
            if (err.code === 'ER_DUP_ENTRY' || err.code == '23505' || err.code == 'SQLITE_CONSTRAINT') {
                return res.status(422).send({ msg: 'The name/email you have entered is already associated with another account.' });
            }
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        });
};

exports.put = (req, res, next)=>{
    req.assert('name', 'Name cannot be blank').notEmpty();
    req.assert('email', 'Email is not valid').isEmail();
    req.assert('email', 'Email cannot be blank').notEmpty();
    req.assert('password', 'Password must be at least 4 characters long').len(4);
    req.sanitize('email').normalizeEmail({ remove_dots: false });
    let errors = req.validationErrors();

    let role = null;
    if(req.body.role){
        if(req.body.role != 'normal' && req.body.role != 'power') {
            if(!errors)
                errors = [];
            errors.push({
                "param": "role",
                "msg": "Role should be equal to 'normal' or 'power'"
            });
        } else if(req.user.get('role') != 'power')
            return res.status(403).send({msg: "You are not authorized to modify roles"});
        else
            role = req.body.role;
    }

    if (errors) {
        return res.status(422).send(errors);
    }

    if (req.user.get('role') != 'power' && req.user.get('id') != req.params.id)
        return res.status(403).send({msg: "You are not authorized to modify this user"});

    let dataToSet = {
        name: req.body.name,
        email: req.body.email,
        password: req.body.password
    };

    if (role)
        dataToSet.role = role;

    return new User({id: req.params.id}).fetch()
        .then(data=>{
            if(!data)
                return res.status(404).send({msg: "User not found"});
            return data.save(dataToSet).then(data=>res.send(data.toJSON()))
        })
        .catch((err) => {
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        });
};

exports.delete = (req, res, next)=>{
    if (req.user.get('role') != 'power' && req.user.get('id') != req.params.id)
        return res.status(403).send({msg: "You are not authorized to modify this user"});

    return new User({id: req.params.id}).fetch()
        .then(data=>{
            if(!data)
                return res.status(404).send({msg: "User not found"});
            return data.destroy().then(res.send(data.toJSON()));
        })
        .catch(err=>{
            console.error(err);
            res.status(500).send({msg: "Internal server Error"});
        })
};

exports.login = (req, res, next) => {
    req.assert('email', 'Email is not valid').isEmail();
    req.assert('email', 'Email cannot be blank').notEmpty();
    req.assert('password', 'Password cannot be blank').notEmpty();
    req.sanitize('email').normalizeEmail({ remove_dots: false });

    let errors = req.validationErrors();

    if (errors) {
        return res.status(422).send(errors);
    }

    let errorMex = ()=>res.status(401).send({ msg: 'Invalid email or password' });
    new User({ email: req.body.email })
        .fetch()
        .then(user => {
            if (!user) {
                return errorMex();
            }
            user.comparePassword(req.body.password, (err, isMatch) => {
                if (!isMatch) {
                    return errorMex();
                }
                return res.send({ token: generateToken(user), user: user.toJSON()});
            });
        });
};
