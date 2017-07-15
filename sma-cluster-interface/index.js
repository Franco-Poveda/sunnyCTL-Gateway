'use strict';

const config = require('config');
const EventEmitter = require('events');

const SMAdigitalInterface = require('./sma-interface');
const amqp = require('./amqp');

const appEnv = process.env.NODE_ENV || 'development';

class Log extends EventEmitter { }
const logger = new Log();
logger.on('info', msg => console.log(msg));

const smaDigitalInterface = new SMAdigitalInterface({ config: config, logger });

amqp.init({ log: logger, config: config.amqp });
amqp.connect()
    .then(conn => amqp.openChannels(conn))
    .then(channels => smaDigitalInterface.start(channels));

