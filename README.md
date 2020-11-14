# Machine Identity

This application demonstrates how machine identity can be created and be used to secure data created by a machine.

## Setup

### Step 1 - Get a Secure Element

If haven't received one please send an email to [hello@steelbutsmart.com](mailto:hello@steelbutsmart.com). 

### Step 2 - Get a Raspberry

1. Get a [Raspberry 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) or [Raspberry 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/) plus possibly some accessories as a case or USB power cable. 
2. Get a MicroSD Card like [SanDisk Ultra 16GB microSDHC with adapter](https://www.amazon.de/SanDisk-Ultra-microSDHC-Speicherkarte-Adapter/dp/B073S9SFK2/).
3. Install Secure Element as illustrated.

![install Secure Element](images/install_secure_element_on_raspberry.png?raw=true "install Secure Element")

### Step 3 - Install and configure Raspian
1. Download [Raspberry Pi Imager](https://www.raspberrypi.org/downloads/).
2. Install latest Raspberry Pi OS.
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

### Step 4 - Clone repository and install dependencies

1. Clone repository with `git clone https://github.com/steelbutsmart/machine-identity`.
2. Install dependencies with `pip3 install --user --requirement requirements.txt`.

## Run the demo

### Step 1 - Create a machine identity
```bash
python3 mi.py -m hello
```
```
Machine Identity of hello
Hash of private key 1dbdfb15257b66108e01f599dcd2c43a3b9c65ead77ae90fe5cb89dbaef91c89
Public key C9XXBFzTeqwQZepkevd9hsHAD1FfpVGkz11MUa5ayAEq stored on R3C in transaction:
https://ipdb-eu2.riddleandcode.com/api/v1/transactions/3ef09cc894543b9ef3fe4f6044409542e8ead139e5d0099d2d40b9f2c53379e8
```
### Step 2 - Lookup the machine identity
```bash
python3 mi.py -l C9XXBFzTeqwQZepkevd9hsHAD1FfpVGkz11MUa5ayAEq
```
```
{
  "data": {
    "id": "C9XXBFzTeqwQZepkevd9hsHAD1FfpVGkz11MUa5ayAEq",
    "Machine": {
      "Name": "hello",
      "Type": "Lucky Puncher",
      "Owner": "Wunderbar GmbH",
      "AddressLine": "Im Gl\u00fcck 1",
      "ZipCode": "4010",
      "City": "Linz"
    },
    "Location": "Halle 8"
  },
  "id": "3ef09cc894543b9ef3fe4f6044409542e8ead139e5d0099d2d40b9f2c53379e8"
}
https://ipdb-eu2.riddleandcode.com/api/v1/transactions/3ef09cc894543b9ef3fe4f6044409542e8ead139e5d0099d2d40b9f2c53379e8
```

### Step 3 - Process data from the machine and store the hash on the blockchain

For demo purposes several sample data files can be found in the directory `source`. Files processed are stored in the directory `database`. A creation date time is added to the data and the SHA256 hash is calculated, which is stored on the blockchain in a transaction. The transaction id serves as primary key in the database record, to which the calculates hash is added.

Input file `data1.json`
```
{
  "id": "8ce64216-a8ef-4998-905b-420e9ec5413d", 
  "description": "This is some data generated by sensors of a machine", 
  "value_1": 1.0, 
  "value_2": false, 
  "value_3": 3.14, 
  "creation_datetime": "2019-10-17T22:07:15.178847"
}
```

```
python3 mi.py -d source/data1.json
```
```
Data in file source/data1.json plus SHA256 hash stored in
database/d0a4528a127209c7c761a3daf14a615a20576644257348f6c3d867a2eeff7a5b.json
Id and SHA256 hash in transaction on R3C
https://ipdb-eu2.riddleandcode.com/api/v1/transactions/d0a4528a127209c7c761a3daf14a615a20576644257348f6c3d867a2eeff7a5b
Id and SHA256 of data
{
  "data": {
    "id": "8ce64216-a8ef-4998-905b-420e9ec5413d",
    "sha": "9b579158b78b6080ab9e39150d22ade1ab57c74319b77904e5bb342006ca8df2"
  }
}
```

Database file `d0a4528a127209c7c761a3daf14a615a20576644257348f6c3d867a2eeff7a5b.json`
```
{
  "data": {
    "id": "8ce64216-a8ef-4998-905b-420e9ec5413d", 
    "description": "This is some data generated by sensors of a machine", 
    "value_1": 1.0, 
    "value_2": false, 
    "value_3": 3.14, 
    "creation_datetime": "2019-10-21T20:23:24.016655"
  }, 
  "sha": "9b579158b78b6080ab9e39150d22ade1ab57c74319b77904e5bb342006ca8df2"
}
````

### Step 4 - Query for records signed by the machine

The public key serves a the unique identifier used to query for transactions in a simple wildcard manner. All transactions signed with this public key are returned.
```
python3 mi.py -q C9XXBFzTeqwQZepkevd9hsHAD1FfpVGkz11MUa5ayAEq
```
```
Transactions
tx_id: 3ef09cc894543b9ef3fe4f6044409542e8ead139e5d0099d2d40b9f2c53379e8
https://ipdb-eu2.riddleandcode.com/api/v1/transactions/3ef09cc894543b9ef3fe4f6044409542e8ead139e5d0099d2d40b9f2c53379e8
```

### Step 5 - Retrieve a database record and check its integrity

The transaction id serves two purposes:
1. Retrieve the data from the database
2. Retrieve the hash calculated at the creation time from the blockchain

The hash of the data is calculated compared with the value stored on the blockchain - if they match the data has not be modified since its creation. Furthermore, the data of the originating machine is displayed.
```
python3 mi.py -r 0f2b4ec3fde44f88146b0b7075ef2f7eaa926d0b097f78a32dbb798e35903420
```
```
Hash calculated from data: 685e2af6705a6a239021703e29952f8d8e2eb46bf84817fff690770de0fd2941
Hash stored in database:   685e2af6705a6a239021703e29952f8d8e2eb46bf84817fff690770de0fd2941
Hash stored on R3C:        685e2af6705a6a239021703e29952f8d8e2eb46bf84817fff690770de0fd2941
Hashes match!
Transaction:
https://ipdb-eu2.riddleandcode.com/api/v1/0f2b4ec3fde44f88146b0b7075ef2f7eaa926d0b097f78a32dbb798e35903420
Data:
{
  "id": "8ce64216-a8ef-4998-905b-420e9ec5413d",
  "description": "This is some data generated by sensors of a machine",
  "value_1": 1.0,
  "value_2": false,
  "value_3": 3.14,
  "creation_datetime": "2019-10-21T21:51:54.748513"
}
Identity of transaction signer:
{
  "data": {
    "id": "H7vrVAvTcPF9BPv2HCKkBGVYE9bRW5PTq364ibFt6eEh",
    "Machine": {
      "Name": "another_test",
      "Type": "Lucky Puncher",
      "Owner": "Wunderbar GmbH",
      "AddressLine": "Im Gl\u00fcck 1",
      "ZipCode": "4010",
      "City": "Linz"
    },
    "Location": "Halle 8"
  },
  "id": "73e0cf09886e5a266062c9840d166fe77d2564ab902334566d3eef85761037f5"
}
https://ipdb-eu2.riddleandcode.com/api/v1/transactions/73e0cf09886e5a266062c9840d166fe77d2564ab902334566d3eef85761037f5
```


### Troubles or Questions?
In case of troubles to get things running please open a Github issue. For all other enquieries send us email at [hello@s1seven.com](mailto:hello@s1seven.com).

### Credits 
Secure Element & [initial code and library](https://github.com/RiddleAndCode/SEAL-SDK) by [Riddle&Code](https://www.riddleandcode.com). Idea and tweaking details by [S1Seven](https://s1seven.com). Code by @dogusriddle.
