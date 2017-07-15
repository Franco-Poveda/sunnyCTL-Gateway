var gpio = require('rpi-gpio');

const setpins = (p ,i) => {

    gpio.write(p, i, function(err) {
        if (err) throw err;
        console.log('Written to pin');

    });
}

gpio.setMode(gpio.MODE_BCM);

gpio.setup(12, gpio.DIR_HIGH, 
() => gpio.setup(16, gpio.DIR_HIGH,
    ()=> gpio.setup(20, gpio.DIR_HIGH,
        () => gpio.setup(21, gpio.DIR_HIGH, 
            setpins(12,false))
    )));
