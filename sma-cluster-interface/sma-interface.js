const PCF8574 = require('pcf8574').PCF8574;
const i2cBus = require('i2c-bus').openSync(1);

const addr = 0x38;


class SMAdigitalInterface {
    constructor({ logger, config }) {

        this.logger = logger;
        this.config = config.get('amqp');
        this.io = config.get('gpio');
        this.pcf = new PCF8574(i2cBus, addr, true);

    }

    start([inCh, outCh]) {
        this.inCh = inCh;
        this.outCh = outCh;
        this.inCh.prefetch(1);
        const channels = this.io.do1.concat(this.io.do2);
        this.setup(channels);

    }
    setup(chs) {
        const setup = chs.map(c => {
            return this.pcf.outputPin(c, false, true);
        });

        Promise.all(setup).then(values => {
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
                return this.pcf.setPin(this.io.do1[i], (state == 0)? false:true);
            }, message.do2.forEach(
                (state, i) => {
                    return this.pcf.setPin(this.io.do2[i], (state == 0)? false:true);
                }),
            this.outCh.publish(
                this.config.out.exchange.name,
                this.config.out.queue.binding,
                new Buffer(msg.content),
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
