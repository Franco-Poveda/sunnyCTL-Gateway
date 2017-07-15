'use strict'

const amqp = require('amqplib');

let log,
    conf;

const init = params => {
    log = params.log;
    conf = params.config;
}

const connect = () => amqp.connect(conf.uri).then(conn => {
    conn.on('error', err => {
        log.emit('info', `[AMQP-ERROR]: [${err.message}]`);
    });

    conn.on('close', () => {
        log.emit('info', '[AMQP-CLOSE]: connection closed');
    });

    log.emit('info', `[AMQP] connected`);

    return conn;
}).catch(err => {
    log.emit('info', `[AMQP-CONECTION_ERROR]: [${err.message}]`);
    throw err;
});

const openOutChannel = amqpConn => amqpConn.createConfirmChannel()
    .then(ch =>
        ch.assertExchange(
            conf.outExchange,
            'topic',
            { autoDelete: false, durable: true}
        )
        .then(() => ch)
    );

const openInChannel = amqpConn => amqpConn.createChannel()
    .then(ch => ch.assertQueue(conf.inQueue, { durable: true })
        .then(_qok => ch.bindQueue(conf.inQueue, conf.bindExchange, conf.bindKey))    
        .then(() => ch));
    
const openChannels = amqpConn => Promise.all([
    openInChannel(amqpConn),
    openOutChannel(amqpConn)
]);

module.exports = {
    connect,
    openChannels,
    init
}