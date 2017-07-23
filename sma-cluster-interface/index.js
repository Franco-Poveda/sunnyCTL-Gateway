'use strict';

const config = require('config');
const logger = require('micro-libs').logger;
const Rabbitmq = require('micro-libs').rabbitmq;

const SMAdigitalInterface = require('./sma-interface');

const appEnv = process.env.NODE_ENV || 'development';
logger.init({ env: appEnv, serviceName: 'sma-cluster-interface' });

const amqp = new Rabbitmq({ logger, config: config.get('amqp') });
amqp.connect()
    .then(conn => amqp.openChannels(conn))
    .then(channels => {
        const smaDigitalInterface = new SMAdigitalInterface({ config, logger });
        smaDigitalInterface.start(channels)
    });

