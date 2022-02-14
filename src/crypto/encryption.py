from abc import ABCMeta, abstractmethod
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from src.config import Config
from src.utils import generate_random
import os


class Encryption(metaclass=ABCMeta):

    label = ""

    @abstractmethod
    def encrypt(self, data) -> tuple:
        """
        Encrypts data,
        generate new key for each data
        :param data: data to encrypt
        :return:  encrypted data and key to decrypt it
        """
        raise NotImplemented

    @abstractmethod
    def decrypt(self, encrypted_data, key):
        """
        Decrypt data with provided key
        :param encrypted_data: data to decrypt
        :param key: decryption key
        :return: decrypted data
        """
        raise NotImplemented

    @staticmethod
    def get_encryptor(filename):
        for encryptor in Encryption.__subclasses__():
            if os.path.exists(encryptor().key_name(filename)):
                return encryptor()
        else:
            raise Exception("Encryptor is not found!")

    @staticmethod
    def get_default_encryptor():
        config = Config()
        encryption_type = config.encryption_type()
        if encryption_type == "aes":
            return SymmetricEncryption()
        elif encryption_type == "hybrid":
            return HybridEncryption()

    def key_name(self, filename):
        key_path = Config().key_path()
        return os.path.join(key_path, f"{filename}.{type(self).label}")


class SymmetricEncryption(Encryption):

    label = "aes"

    def encrypt(self, data):
        session_key = generate_random(16).encode()[:16]
        aes = AES.new(session_key, AES.MODE_EAX)
        data, tag = aes.encrypt_and_digest(data.encode())
        encrypted_data = [aes.nonce, tag, data]
        return encrypted_data, session_key

    def decrypt(self, encrypted_data, session_key):
        nonce, tag, data = encrypted_data
        aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = aes.decrypt_and_verify(data, tag)
        return data.decode()


class HybridEncryption(Encryption):

    label = "hybrid"

    def __init__(self):
        self.symmetric_encryption = SymmetricEncryption()
        key_path = Config().key_path()
        key_path = os.path.join(key_path, "key.pem")
        if os.path.exists(key_path):
            with open(key_path) as key:
                self.rsa_key = RSA.import_key(key.read())
        else:
            random_generator = Random.new().read
            self.rsa_key = RSA.generate(1024, random_generator)
            with open(key_path, "w") as file:
                file.write(self.rsa_key.export_key("PEM").decode())
        self.public_crypter = PKCS1_OAEP.new(self.rsa_key)

    def encrypt(self, data) -> tuple:
        encrypted_data, session_key = self.symmetric_encryption.encrypt(data)
        session_key = self.public_crypter.encrypt(session_key)
        return encrypted_data, session_key

    def decrypt(self, encrypted_data, session_key):
        session_key = self.public_crypter.decrypt(session_key)
        data = self.symmetric_encryption.decrypt(encrypted_data, session_key)
        return data
