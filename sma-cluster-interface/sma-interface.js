const gpio = require('rpi-gpio');


class SMAdigitalInterface {
    constructor({ logger, config }) {

        this.logger = logger;
        this.config = config.get('amqp');
        this.io = config.get('gpio');


    }

    start([inCh, outCh]) {
        this.inCh = inCh;
        this.outCh = outCh;
        this.inCh.prefetch(1);
        gpio.setMode(gpio.MODE_BCM);

        const channels = this.io.do1.concat(this.io.do2);
        const direction = gpio.DIR_HIGH;
        this.setup(channels, direction);

    }
    setup(chs, dir = gpio.MODE_BCM) {
        const setup = chs.map(c => {
            return new Promise((resolve, reject) => {
                return gpio.setup(c, dir, (err) => {
                    if (err)
                        return reject(err);
                    return resolve('true');
                });
            });
        });

        Promise.all(setup).then(values => {
            this.logger.emit('debug', values);

            this.inCh.consume(this.config.in.queue.name, this.handleMessage.bind(this), { noAck: false })

        }).catch(reason => {
            throw reason;
        });
    }
    handleMessage(msg) {

        const message = JSON.parse(msg.content.toString());
        this.logger.emit('debug', message);
        message.do1.forEach(
            (state, i) => {
                gpio.write(this.io.do1[i], state, function (err) {
                    if (err) throw err;
                    return;
                });
            }, message.do2.forEach(
                (state, i) => {
                    gpio.write(this.io.do2[i], state, function (err) {
                        if (err) throw err;
                        return;
                    });
                }),
            this.outCh.publish(
                this.config.out.exchange.name,
                this.config.out.queue.binding,
                new Buffer(JSON.stringify(msg.content)),
                {}, (err) => {
                    if (err) {
                        this.logger.emit("info", "PUBLISH_ERR: " + err);
                    }
                    this.logger.emit('info', 'New values wrote and spread');

                    this.inCh.ack(msg);

                })
        );
    }
}

module.exports = SMAdigitalInterface;

