# AES/ECB/PKCS7Padding
from Crypto.Cipher import AES


class AES256Crypter(object):
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_ECB
        self.cipher = AES.new(self.key, self.mode)

    def pkcs7padding(self, data):
        padding = AES.block_size - len(data)
        return data + chr(padding) * padding

    def pkcs7unpadding(self, data):
        unpadding = data[15]
        return data[0:16 - unpadding]

    def encrypt(self, data):
        data = self.pkcs7padding(data)
        encrypted = self.cipher.encrypt(data.encode())
        return ''.join(["%02x" % x for x in encrypted]).strip()

    def decrypt(self, data):
        encrypted = bytes.fromhex(data)
        unencrypted = self.cipher.decrypt(encrypted)
        return self.pkcs7unpadding(unencrypted).decode()
