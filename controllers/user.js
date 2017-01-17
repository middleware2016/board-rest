/**
 * Created by claudio on 17/01/17.
 */
"use strict";
let User = require('../models/User');

exports.list = (req, res, next)=>{
    "use strict";
     User.fetchAll()
        .then(data=>res.send(data.toJSON()))
        .catch(err=>{
            console.error(err);
            res.status(500).send({msg: "Internal server Error"})
        })
};