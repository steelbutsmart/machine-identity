import ctypes
import base58
import binascii
DEBUG = False


class SEAL:



    def __init__(self, library_path=None):
        """
        Args:
            library_path <str> : Full path to the compiled file of microECC library (libmicroecc.so)
            curve_name <str> : "secp256r1" (default), "secp160r1", "secp192r1", "secp224r1", "secp256k1"
        """
        self.result = -1
        self.lib = ctypes.CDLL(library_path or 'libseadyn.so')
        self.se_init = self.wrap_function(self.lib,"se_init",ctypes.c_int,[ctypes.c_int])
        self.se_save_key_pair = self.wrap_function(self.lib,"se_save_key_pair",ctypes.c_int,[ctypes.c_uint8,ctypes.POINTER(ctypes.c_ubyte),ctypes.c_uint16,ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint16])
        self.se_get_random =self.wrap_function(self.lib,"se_get_random",ctypes.c_int,[ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint8])
        self.se_write_data =self.wrap_function(self.lib,"se_write_data",ctypes.c_int,[ctypes.c_uint8,ctypes.POINTER(ctypes.c_ubyte),ctypes.c_uint8])
        self.se_read_data =self.wrap_function(self.lib,"se_read_data",ctypes.c_int,[ctypes.c_ushort,ctypes.POINTER(ctypes.c_uint8),ctypes.c_ushort])
        self.se_get_pubkey =self.wrap_function(self.lib,"se_get_pubkey",ctypes.c_int,[ctypes.c_uint8,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_ushort)])
        self.se_get_sha256 =self.wrap_function(self.lib,"se_get_sha256",ctypes.c_int,[ctypes.c_char_p,ctypes.c_uint8,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8)])
        self.se_close= self.wrap_function(self.lib,"se_close",ctypes.c_int,[])

       # self.lib.se_init.argtypes = [ctypes.c_int]
        result = self.se_init(ctypes.c_int(0))
        if result != 0:
            raise Exception('Init failed')
        else:
            if DEBUG:
                print("SE Init Success\n")


    def wrap_function(self,lib, funcname, restype, argtypes):
        """Simplify wrapping ctypes functions"""
        func = lib.__getattr__(funcname)
        func.restype = restype
        func.argtypes = argtypes
        return func

    def close_comms(self):
        result = self.se_close()
        if result != 0:
            raise Exception('i2c close failed')
        else:
            if DEBUG:
                print("SE se_close Success\n")

    def get_random(self):
        random_buffer = ((ctypes.c_uint8) * 32 )()
        result = self.se_get_random(random_buffer,32)
        if result != 0:
            raise Exception('rnd generation failed')
        else:
            if DEBUG:
                print("SE se_get_random Success\n")
        return random_buffer


    def save_keypair(self,pubKey,secret):
        nullptr = ((ctypes.c_uint8) * 1 )()
        result = self.se_save_key_pair(10,(ctypes.c_ubyte*32).from_buffer_copy(base58.b58decode(pubKey)),0,nullptr,0)
        if result != 0:
            raise Exception('se_save_key_pair failed')
        else:
            self.store_data(0,(ctypes.c_ubyte*32).from_buffer_copy(base58.b58decode(secret)),32)
            if DEBUG:
                print("SE se_save_key_pair Success\n")

    def store_data(self,offset,data,datalen):
        result = self.se_write_data(offset,data,datalen)
        if result != 0:
            raise Exception('rnd generation failed')
        else:
            if DEBUG:
                print("SE se_write_data Success\n")


    def read_data(self,offset,datalen):

        data = ((ctypes.c_uint8) * datalen )()
        result = self.se_read_data(offset,data,datalen)
        if result != 0:
            raise Exception('read_data failed')
        else:
            if DEBUG:
                print("SE se_read_data Success\n")
        return bytes(data)

    def get_public_key(self):
        pubKey = ((ctypes.c_uint8) * 64 )()
        nullptr = ((ctypes.c_ushort) * 1 )()
        result = self.se_get_pubkey(10,pubKey,nullptr)
        if result != 0:
            raise Exception('get_public_key failed')
        else:
            if DEBUG:
                print("SE se_get_pubkey Success\n")
        return bytes(bytearray(pubKey)[:32])

    def get_hash(self,data,dataLen):
        b_data = str(data).encode('utf-8')
        sha = ((ctypes.c_uint8) * 32 )()
        shaLen = ((ctypes.c_uint8) * 2 )(32)
        result = self.se_get_sha256(b_data,dataLen,sha,shaLen)
        if result != 0:
            raise Exception('get_hash failed')
        else:
            if DEBUG:
                print("SE se_get_sha256 Success\n")
        return bytes(sha)