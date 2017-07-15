const gpio = require('rpi-gpio');


class SMAdigitalInterface {
    constructor({ logger, config }) {
        this.logger = logger;
        this.config = config.amqp;
        this.do1 = config.gpio.do1;
        this.do2 = config.gpio.do2;

        gpio.setMode(gpio.MODE_BCM);
        const setupDO1 = this.do1.map(p => {
            return new Promise((resolve, reject) => {
                return gpio.setup(p, gpio.DIR_HIGH, (err) => {
                    if (err)
                        reject(err);
                    resolve();
                });
            });
        });
        const setupDO2 = this.do2.map(p => {
            return new Promise((resolve, reject) => {
                return gpio.setup(p, gpio.DIR_HIGH, (err) => {
                    if (err)
                        reject(err);
                    resolve();
                });
            });
        });

        Promise.all(setupDO1).then(values => {
            console.log(values);
        }).catch(reason => {
            console.log(reason)
        });

        Promise.all(setupDO2).then(values => {
            console.log(values);
        }).catch(reason => {
            console.log(reason)
        });
    }

    start([inCh, outCh]) {
        this.inCh = inCh;
        this.outCh = outCh;
        this.inCh.prefetch(1);
        return this.inCh.consume(this.config.inQueue, this.handleMessage.bind(this), { noAck: false });
    }
    handleMessage(msg) {

        const message = JSON.parse(msg.content.toString());
        console.log(message);
        message.do1.forEach(
            (state, i) => {
                gpio.write(this.do1[i], state, function (err) {
                    if (err) throw err;
                    console.log('Written to pin');
                    return;
                });
            }, message.do2.forEach(
                (state, i) => {
                    gpio.write(this.do2[i], state, function (err) {
                        if (err) throw err;
                        console.log('Written to pin');
                        return;
                    });
                }), this.inCh.ack(msg));
    }
}

module.exports = SMAdigitalInterface;

