"""
Copyright (c) 2021 Philipp Scheer
"""


from Crypto.Cipher import AES
from Crypto.Random import new as Random
from hashlib import sha256
import os
import rsa
import base64
import multiprocessing


class Encryption:
    @staticmethod
    def generateKeyPair(keysize):
        return rsa.newkeys(keysize, poolsize=multiprocessing.cpu_count())

    @staticmethod
    def exportKey(key):
        return key.save_pkcs1().decode('utf8')

    @staticmethod
    def loadPublic(pem):
        return rsa.PublicKey.load_pkcs1(pem)

    @staticmethod
    def loadPrivate(pem):
        return rsa.PrivateKey.load_pkcs1(pem)

    @staticmethod
    def encrypt(message: bytes, publicKey):
        return rsa.encrypt(message, publicKey)

    @staticmethod
    def decrypt(encryptedMessage: bytes, privateKey):
        return rsa.decrypt(encryptedMessage, privateKey)

    @staticmethod
    def sign(message: bytes, privateKey, hash: str="SHA-512") -> bytes:
        return rsa.sign(message, privateKey, hash)

    @staticmethod
    def verify(message: bytes, signature, publicKey):
        try:
            rsa.verify(message, signature, publicKey)
            return True
        except Exception:
            return False

    @staticmethod
    def encapsulate(message: str, remotePublicKey, localPrivateKey):
        key = os.urandom(75) # depends on the remotePublicKey size... 1024 is min, so min 86 bytes
        signature: str = base64.b64encode(Encryption.sign(message.encode("utf-8"), localPrivateKey)).decode("utf-8")
        ciphered_data: str = base64.b64encode(AESCipher(f"{signature}${message}", key).encrypt()).decode("utf-8")
        encrypted_key: str = base64.b64encode(Encryption.encrypt(key, remotePublicKey)).decode("utf-8")
        final_data = f"{encrypted_key}${ciphered_data}"
        return final_data

    @staticmethod
    def decapsulate(data, remotePublicKey, localPrivateKey, mustHaveValidSignature: bool=True):
        encrypted_key, ciphered_data = data.split("$")
        original_key = Encryption.decrypt(base64.b64decode(encrypted_key), localPrivateKey)
        unciphered_data: str = AESCipher(base64.b64decode(ciphered_data), original_key).decrypt()
        signature, message = unciphered_data.split("$", 1)
        if not mustHaveValidSignature:
            print("WARNING: MESSAGE WAS NOT VERIFIED!")
            return message
        if Encryption.verify(message.encode("utf-8"), base64.b64decode(signature), remotePublicKey):
            return message
        else:
            raise Exception("Invalid Signature")


class AESCipher:
    def __init__(self, data, key):
        self.block_size = 16
        self.data = data
        self.key = sha256(key).digest()[:32]
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * chr (self.block_size - len(s) % self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self):
        plain_text = self.pad(self.data)
        iv = Random().read(AES.block_size)
        cipher = AES.new(self.key,AES.MODE_OFB,iv)
        return iv + cipher.encrypt(plain_text.encode())

    def decrypt(self):
        cipher_text = self.data
        iv = cipher_text[:self.block_size]
        cipher = AES.new(self.key,AES.MODE_OFB,iv)
        return self.unpad(cipher.decrypt(cipher_text[self.block_size:])).decode()
