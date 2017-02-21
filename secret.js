/**
 * Created by claudio on 21/02/17.
 */
let crypto = require('crypto');
console.log('Secret: '+crypto.randomBytes(32).toString('hex'));