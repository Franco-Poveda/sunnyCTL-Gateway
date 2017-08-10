var mqtt = require('mqtt')
const config = require('config');
var client = mqtt.connect({ port: 1883, host: 'sunnyctl.povedaingenieria.com', keepalive: 10000, username: 'sctl', password: 'sctl' });


const EventEmitter = require('events');
const amqp = require('./amqp');

const appEnv = process.env.NODE_ENV || 'development';

class Log extends EventEmitter { }
const logger = new Log();
logger.on('info', msg => console.log(msg));

var currState = "";
amqp.init({ log: logger, config: config.amqp });
amqp.connect()
    .then(conn => amqp.openChannels(conn))
    .then(channels => {
        channels[0].consume(config.amqp.inQueue, msg => {
            currState = JSON.parse(msg.content.toString());
            console.log("got new state, passing to PaaS");
            channels[0].ack(msg);
        },{"noAck": false});

        client.on('connect', function () {
            console.log('MQTT connected');
            client.subscribe('params')
            client.publish('controller', new Buffer(JSON.stringify(currState)))


        });

        client.on('message', function (topic, message) {
            console.log('request.body: ' + message.toString());
            state = message.toString();
            client.publish('controller', '{"state":' + state + '}')
            channels[1].publish('tasks', 'write', new Buffer(message));

        });

    });
