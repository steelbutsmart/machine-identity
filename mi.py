import base58
from SEAL import SEAL
from bigchaindb.common.crypto import key_pair_from_ed25519_key
from bigchaindb_driver.crypto import generate_keypair
from cryptoconditions import crypto
from bigchaindb_driver import BigchainDB
from collections import namedtuple
import binascii
import os
import json
import sys, getopt

CryptoKeypair = namedtuple('CryptoKeypair', ('private_key', 'public_key'))
current_dir = os.path.dirname(os.path.abspath(__file__))
bdb_root_url = 'https://ipdb-eu2.riddleandcode.com'



def generate_identity(se):
    rnd = se.get_random()
    rndHex = (binascii.hexlify(rnd)).decode()
    CryptoKeypair = key_pair_from_ed25519_key(rndHex)
    SECRET=CryptoKeypair.private_key
    PUBLIC=CryptoKeypair.public_key
    se.save_keypair(PUBLIC,SECRET)
    print("Hash of priv key :")
    print(se.get_hash(SECRET,len(SECRET)).hex())
    print("pub key :")
    print(PUBLIC)

def read_identity(se):
    return CryptoKeypair(private_key=str(base58.b58encode(se.read_data(0,32)).decode()),
                         public_key=str(base58.b58encode(se.get_public_key()).decode()))

def hash_data_sources(se,paths,id):

    file = open(paths,"r")
    content = file.read()
    content_size = len(content)
    sha = se.get_hash(content,content_size)
    print(sha.hex())

    with open(paths) as f:
        data = json.load(f)
        f.close()

    a_dict = {'sha256': sha.hex()}
    data.update(a_dict)
    with open("database/"+id, 'w') as f:
        json.dump(data, f)
        f.close()

def prepare_outputs(se,id,file):
    print("\nHashing "+ file+ "\n")
    hash_data_sources(se,"source/"+file,id)

def attest_device(device_name,pair):
    data_sources = {
        'data': {
            "devices" :device_name
        },
    }
    prepared_token_tx = bdb.transactions.prepare(
        operation='CREATE',
        metadata={"ID":"Attestation of "+ device_name},
        signers=pair.public_key,
        recipients=[([pair.public_key], 10)],
        asset=data_sources)
    print("prepared_token_tx")

    # fulfill and send the transaction
    fulfilled_token_tx = bdb.transactions.fulfill(
        prepared_token_tx, private_keys=pair.private_key)
    print("fulfilled_token_tx")

    bdb.transactions.send_commit(fulfilled_token_tx)


def send_data_blockchain(se,device_name,pair,file):
    data_sources = {
        'data': {
            "devices" :device_name
        },
    }
    path = "source/" + file
    f = open(path,"r")
    content = f.read()
    f.close()
    content_size = len(content)
    sha = se.get_hash(content,content_size)
    prepared_token_tx = bdb.transactions.prepare(
        operation='CREATE',
        metadata={"SHA":sha.hex()},
        signers=pair.public_key,
        recipients=[([pair.public_key], 10)],
        asset=data_sources)

    # fulfill and send the transaction
    fulfilled_token_tx = bdb.transactions.fulfill(
        prepared_token_tx, private_keys=pair.private_key)

    prepare_outputs(se,fulfilled_token_tx["id"],file)

    tx=bdb.transactions.send_commit(fulfilled_token_tx)
    print("\n... TX SENT ...\n")
    print(tx)

bdb = BigchainDB(bdb_root_url)

def main(argv):

    # if len(sys.argv) <= 1:
    #     opts.append('h')
    raspberry = SEAL(current_dir+"/libseadyn.so")
    inputfile = ''

    if not os.path.exists('database'):
        os.makedirs('database')
    try:
        opts, args = getopt.getopt(argv,"cQqsghi:",["ifile="])
    except getopt.GetoptError:
        print ('\n\tUsage : python3 mi.py -i <ID>\n\n \
        \r\trun python3 mi.py - h for HELP.\n')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('\n\tUsage : python3 mi.py -i <ID> -s\n \
            \r\t\tpython3 mi.py -i <ID> -q \n \
            \r\t\tpython3 mi.py -g\n \
            \r COMMANDS:\n\n \
            \r   -i\t:  id of the device to attest to the blockchain.\n \
            \r   -g\t:  generate a new ED25519 key-pair & store on the SECURE-ELEMENT.\n \
            \r   -s\t:  hash the file under ./source save the result under ./database with TX-ID name and send the digest to the blockchain.\n \
            \r   -q\t:  to querry the blockchain with the <ID> for matching transaction under this name and list them by the TRANSACTION-ID.\n \
            \r   -Q\t:  Get the full transaction details for all the transactions with the matching <ID>\n \
            \r   -c\t:  Check the hash values in ./database against the values get from the blockchain.\n ')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt == '-g':
            generate_identity(raspberry)
            sys.exit()
        elif opt == '-s':
            if len(sys.argv) <= 1 or not inputfile:
                print ('\n\tUsage : python3 mi.py -i <ID>\n\t<ID> can not be empty !\n')
                sys.exit(2)
            else:
                pair = read_identity(raspberry)
                print(pair.private_key)
                print(pair.public_key)

                data_lists = os.listdir(current_dir + "/source")

                for data in data_lists:
                    send_data_blockchain(raspberry,inputfile,pair,data)
        elif opt == '-q':
            tx_ids = set()
            if len(sys.argv) <= 1 or not inputfile:
                print ('\n\tUsage : python3 mi.py -i <ID>\n\t<ID> can not be empty !\n')
                sys.exit(2)
            TX = bdb.assets.get(search=inputfile)
            print("TX ids with the asset name "+inputfile +" in it.\n")
            for i,x in zip(range(len(TX)),TX):
                tx_ids.add(x["id"])
            print(tx_ids)
            print("\n\n")
            sys.exit()
        elif opt == '-Q':
            tx_ids = set()
            if len(sys.argv) <= 1 or not inputfile:
                print ('\n\tUsage : python3 mi.py -i <ID>\n\t<ID> can not be empty !\n')
                sys.exit(2)
            TX = bdb.assets.get(search=inputfile)
            print("\n\nTX ids with the asset name "+inputfile +" in it.\n")
            for i,x in zip(range(len(TX)),TX):
                tx_ids.add(x["id"])
            for x in tx_ids:
                full_tx = bdb.transactions.retrieve(txid=x)
                print(full_tx)
                print("\n")
            sys.exit()
        elif opt == '-c':
            tx_ids = os.listdir(current_dir + "/database")
            if not tx_ids:
                print("\nNo outpul file found. Exiting ...\n")
                sys.exit()
            print("\n")
            print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
            for x in tx_ids:
                full_tx = bdb.transactions.retrieve(txid=x)
                print("SHA value under transaction-id "  + x + " : " + full_tx["metadata"]["SHA"] + "\n\n")

                with open("database/"+x) as jsonfile:
                    data = json.load(jsonfile)

                print("SHA value under file " + "database/" + x + " : " + data["sha256"]+ "\n\n")
                if full_tx["metadata"]["SHA"] != data["sha256"]:
                    print("\nSHA contents on the database and the blockchain doesn`t match ! Aborting ... \n\n")
                    sys.exit(2)
                print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
            print("\t\tHashes match for all the files under ./database\n\n \
            \t\t     ... TESTS PASSED ...\n\n")
            sys.exit()
    if len(sys.argv) <= 1:
        print ('\n\tUsage : python3 mi.py -i <ID> -s\n \
        \r\t\tpython3 mi.py -i <ID> -q \n \
        \r\t\tpython3 mi.py -g\n \
        \r COMMANDS:\n\n \
        \r   -i\t:  id of the device to attest to the blockchain.\n \
        \r   -g\t:  generate a new ED25519 key-pair & store on the SECURE-ELEMENT.\n \
        \r   -s\t:  hash the file under ./source save the result under ./database with TX-ID name and send the digest to the blockchain.\n \
        \r   -q\t:  to querry the blockchain with the <ID> for matching transaction under this name and list them by the TRANSACTION-ID.\n \
        \r   -Q\t:  Get the full transaction details for all the transactions with the matching <ID>\n \
        \r   -c\t:  Check the hash values in ./database against the values get from the blockchain.\n ')
    raspberry.close_comms()


if __name__ == "__main__":
   main(sys.argv[1:])










