import argparse
import base58
from SEAL import SEAL
from bigchaindb.common.crypto import key_pair_from_ed25519_key
from bigchaindb_driver import BigchainDB
from collections import namedtuple
import hashlib
import binascii
import datetime
import os
import json

CryptoKeypair = namedtuple('CryptoKeypair', ('private_key', 'public_key'))
current_dir = os.path.dirname(os.path.abspath(__file__))
R3C_ROOT_URL = 'https://ipdb-eu2.riddleandcode.com'
r3c = BigchainDB(R3C_ROOT_URL)
secure_element = SEAL(current_dir+"/libseadyn.so")


def create_machine_identity(machine):
    randomHEX = (binascii.hexlify(secure_element.get_random())).decode()
    CryptoKeypair = key_pair_from_ed25519_key(randomHEX)
    secure_element.save_keypair(CryptoKeypair.public_key,
                                CryptoKeypair.private_key)
    asset = {
        'data': {
            'id': CryptoKeypair.public_key,
            "Machine": {
                "Name": machine,
                "Type": "Lucky Puncher",
                "Owner": "Wunderbar GmbH",
                "AddressLine": "Im Glück 1",
                "ZipCode": "4010",
                "City": "Linz",
            },
            "Location": "Halle 8"
        }
    }
    prepared_token_tx = r3c.transactions.prepare(
        operation="CREATE",
        metadata=None,
        signers=CryptoKeypair.public_key,
        recipients=[([CryptoKeypair.public_key], 10)],
        asset=asset)
    fulfilled_token_tx = r3c.transactions.fulfill(
        prepared_token_tx, private_keys=CryptoKeypair.private_key)
    tx = r3c.transactions.send_commit(fulfilled_token_tx)
    print("Machine Identity of " + machine)
    print("Hash of private key " +
          secure_element.get_hash(CryptoKeypair.private_key).hex())
    print("Public key " + CryptoKeypair.public_key +
          " stored on R3C in transaction:")
    print(R3C_ROOT_URL + "/api/v1/transactions/" + tx['id'])
    print(json.dumps(tx["asset"], indent=2))


def lookup_machine(public_key):
    tx = r3c.assets.get(search=public_key)
    print(json.dumps(tx[0], indent=2))
    print(R3C_ROOT_URL + "/api/v1/transactions/" + tx[0]["id"])


def get_identity(se):
    return CryptoKeypair(
        private_key=str(base58.b58encode(se.read_data(0, 32)).decode()),
        public_key=str(base58.b58encode(se.get_public_key()).decode())
    )


def read_and_sign_source_data(source):
    machine = get_identity(secure_element)
    with open(source) as f:
        data = json.load(f)
        f.close()
    data.update({"creation_datetime": datetime.datetime.utcnow().isoformat()})
    sha256 = secure_element.get_hash(json.dumps(data))
    record = {
       "data": data,
       "sha256": sha256.hex() 
    }
    asset = {
        "data": {
            "id": data["id"],
            "sha": sha256.hex()
        },
    }
    prepared_token_tx = r3c.transactions.prepare(
        operation='CREATE',
        metadata=None,
        signers=machine.public_key,
        recipients=[([machine.public_key], 10)],
        asset=asset
    )
    fulfilled_token_tx = r3c.transactions.fulfill(
        prepared_token_tx, private_keys=machine.private_key)
    tx = r3c.transactions.send_commit(fulfilled_token_tx)
    with open("database/" + tx['id'] + ".json", "w") as f:
        json.dump(record, f)
        f.close()
    print("Data in file " + source + " plus SHA256 hash stored in")
    print("database/" + fulfilled_token_tx['id'] + ".json")
    print("Id and SHA256 hash in transaction on R3C")
    print(R3C_ROOT_URL + "/api/v1/transactions/" + tx['id'])
    print("Id and SHA256 of data")
    print(json.dumps(tx["asset"], indent=2))


def query_for_data(public_key):
    tx_ids = set()
    tx = r3c.assets.get(search=public_key)
    print(tx)
    for i, x in zip(range(len(tx)), tx):
        tx_ids.add(x["id"])
    print("Transactions")
    for i in tx_ids:
        print("tx_id: " + i)
        print(R3C_ROOT_URL + "/api/v1/transactions/" + i + "\n")


def retrieve_data(transaction):
    tx = r3c.transactions.retrieve(txid=transaction)
    sha_stored_on_R3C = tx["asset"]["data"]["sha"]
    public_key_signer = tx["outputs"][0]["public_keys"][0]
    record = "database/" + transaction + ".json"
    with open(record) as f:
        record = json.load(f)
        f.close()
    sha_stored_in_db = record['sha256']
    sha_calculated = hashlib.sha256(json.dumps(record["data"]).encode('utf-8')).hexdigest()
    print("Hash calculated from data: " + sha_calculated)
    print("Hash stored in database:   " + sha_stored_in_db)
    print("Hash stored on R3C:        " + sha_stored_on_R3C)
    if sha_calculated == sha_stored_in_db == sha_stored_on_R3C:
        print("Hashes match!\n")
    else:
        print("ATTENTION! Hashes do not match!\n")
    print("Transaction:\n" + R3C_ROOT_URL + "/api/v1/" + tx['id'])
    print("Data:\n" + json.dumps(record['data'], indent=2))
    print("Identity of transaction signer:")
    lookup_machine(public_key_signer)


parser = argparse.ArgumentParser()
parser.add_argument("-m", metavar="name",
                    help="Creates a machine identity with <name> and attests it on R3C")
parser.add_argument("-d", metavar="source", 
                    help="Reads data from file <source> and stores hash signed by machine on R3C")
parser.add_argument("-q", metavar="public_key", 
                    help="queries R3C for transactions signed by machine with <public_key>")
parser.add_argument("-l", metavar="public_key",
                    help="lookup machine descrption for machine with <public_key")
parser.add_argument("-r", metavar="tx", 
                    help="gets and verifies data identified by R3C transaction <tx>")
args = parser.parse_args()

if args.m is not None:
    create_machine_identity(args.m)
elif args.d is not None:
    read_and_sign_source_data(args.d)
elif args.q is not None:
    query_for_data(args.q)
elif args.r is not None:
    retrieve_data(args.r)
elif args.l is not None:
    lookup_machine(args.l)
else:
    parser.print_help()
