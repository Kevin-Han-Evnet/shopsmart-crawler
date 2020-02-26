from Crypto.Cipher import AES
import base64
import hashlib

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-s[-1]]

class HashUtils :

    def getUnHashedPwd (key_32, key_16, hashed_pwd) :

        cipher = AES.new(str(key_32).encode('utf8'), AES.MODE_CBC, IV=str(key_16).encode('utf8'))
        deciphed = cipher.decrypt(base64.b64decode(str(hashed_pwd)))
        deciphed = unpad(deciphed)

        return str(deciphed)[2:-1]


class SmLogger :

    uiTarget = None

    def __init__ (self) :
        pass

    def info (self, msg) :
        print (msg)
        if (self.uiTarget is not None) :
            self.uiTarget.updateMSG (msg)
