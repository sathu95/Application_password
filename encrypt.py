from Crypto.Cipher import AES # used for encryption
import base64 # used for encryption
import os
import logging

import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key):
        self.bs = 32 # the bit size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw) # pad the raw input
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)) # base 64 to return non high ascii chars

    def decrypt(self, enc):
        enc = base64.b64decode(enc) # un base 64 the input to
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs) # pad to bit size

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

class Encrypt:

    key = ""

    def __init__(self):
        self.key = "abcynhf56fghbnf43dsaqw8iknbsdcx4"

    def _fileGetContents(self, filename):
        if os.path.exists(filename):
            fp = open(filename, "r")
            content = fp.read()
            fp.close()
            return content

    #  Ensure key matches AES requirements and is 32 chars in length
    def _generateKey(self, s):
        s = s[:32] # ensure key is 32 chars long at max

        return s

    def encryptString(self, s, salt = ""):
        #return s
        saltedKey = self._generateKey(str(salt) + self.key)
        aes = AESCipher(saltedKey)

        return aes.encrypt(s)


    def decryptString(self, s, salt = ""):
        #return s
        saltedKey = self._generateKey(str(salt) + self.key)
        logging.info(saltedKey)
        aes = AESCipher(saltedKey)

        return aes.decrypt(s)