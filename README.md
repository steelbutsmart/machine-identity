# Machine Identity

**TODO**: write a little intro what we want to show. 

## Setup

### Step 1 - Get a Raspberry

1. Get a [Raspberry 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) or [Raspberry 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/) plus possibly some accessories as a case or USB power cable. 
2. Get a MicroSD Card like [SanDisk Ultra 16GB microSDHC with adapter](https://www.amazon.de/SanDisk-Ultra-microSDHC-Speicherkarte-Adapter/dp/B073S9SFK2/).
3. Install Secure Element as illustrated.

**TODO**: add image with instructions how to plugin secure element.

### Step 2 - Install and configure Raspian
1. Download [balenaEtcher](https://www.balena.io/etcher/).
2. Download and install [Raspian](https://www.raspberrypi.org/downloads/raspbian/).
3. Enable I2C
    1. Run `sudo raspi-config`.
    2. Use the down arrow to select `5 Interfacing Options`.
    3. Arrow down to `P5 I2C`.
    4. Select `yes` when it asks you to enable SPI,
    5. Also select `yes` if it asks about automatically loading the kernel module.
    6. Use the right arrow to select the `<Finish>` button.
    7. Select `yes` when it asks to reboot.
    8. After reboot login and enter `ls /dev/*i2c*`.
    9. Response should be `/dev/i2c-1`.
    
    ![enable I2C interface](images/enable_I2C_interface.png?raw=true "enable I2C interface")

### Step 3 - Clone repository and install dependencies

1. Clone repository with `git clone https://github.com/steelbutsmart/machine-identity`.
2. Install dependencies with `pip3 install bigchaindb`.

## Run the demo


**TODOs**: Add code and instructions to run the demo (Coming mid of October).

### Troubles or Questions?
In case of troubles to get things running please open a Github issue. For all other enquieries send us email at [hello@steelbutsmart.com](mailto:hello@steelbutsmart.com).

### Credits 
Secure Element by [Riddle&Code](https://www.riddleandcode.com).
Code by @dogusriddle.