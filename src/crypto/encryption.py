from abc import ABCMeta, abstractmethod
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from src.config import Config
from src.utils import generate_random
from typing import Tuple
import os


class Encryption(metaclass=ABCMeta):

    label = ""

    @property
    def key_path(self):
        return Config().key_path()

    @abstractmethod
    def encrypt(self, data) -> Tuple[bytes, bytearray]:
        """
        Encrypts data,
        generate new key for each data
        :param data: data to encrypt
        :return:  encrypted data and key to decrypt it
        """
        raise NotImplemented

    @abstractmethod
    def decrypt(self, encrypted_data, key) -> str:
        """
        Decrypt data with provided key
        :param encrypted_data: data to decrypt
        :param key: decryption key
        :return: decrypted data
        """
        raise NotImplemented

    @staticmethod
    def get_encryptor(filename):
        current_encryptor = None
        for encryptor in Encryption.__subclasses__():
            if os.path.exists(encryptor().key_name(filename)):
                if not current_encryptor:
                    current_encryptor = encryptor()
                else:
                    raise Exception("More than one encryptor is found!")
        if current_encryptor:
            return current_encryptor
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
        key_path = self.key_path
        return os.path.join(key_path, f"{filename}.{type(self).label}")

    @staticmethod
    def get_encryptor_by_label(label):
        for encryptor in Encryption.__subclasses__():
            if encryptor().label == label:
                return encryptor()


class SymmetricEncryption(Encryption):

    label = "aes"

    def encrypt(self, data):
        key = generate_random(16).encode()
        aes = AES.new(key, AES.MODE_EAX)
        encrypted_data, tag = aes.encrypt_and_digest(data.encode())
        session_key = bytearray(aes.nonce)
        session_key.extend(bytearray(tag))
        session_key.extend(bytearray(key))
        return encrypted_data, session_key

    def decrypt(self, encrypted_data, session_key):
        n = 16
        session_key = bytearray(session_key)
        nonce, tag, session_key = [bytes(session_key[i:i + n]) for i in range(0, len(session_key), n)]
        aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = aes.decrypt_and_verify(encrypted_data, tag)
        return data.decode()


class HybridEncryption(Encryption):

    label = "hybrid"

    def __init__(self):
        self.symmetric_encryption = SymmetricEncryption()
        key_path = self.key_path
        self.pem_key_path = os.path.join(key_path, "key.pem")
        self._rsa_key = None

    @property
    def rsa_key(self):
        if os.path.exists(self.pem_key_path):
            with open(self.pem_key_path) as key:
                self._rsa_key = RSA.import_key(key.read())
        else:
            random_generator = Random.new().read
            self._rsa_key = RSA.generate(1024, random_generator)
            with open(self.pem_key_path, "w") as file:
                file.write(self._rsa_key.export_key("PEM").decode())
        return PKCS1_OAEP.new(self._rsa_key)

    def encrypt(self, data):
        encrypted_data, session_key = self.symmetric_encryption.encrypt(data)
        session_key = self.rsa_key.encrypt(session_key)
        return encrypted_data, session_key

    def decrypt(self, encrypted_data, session_key):
        session_key = self.rsa_key.decrypt(bytearray(session_key))
        data = self.symmetric_encryption.decrypt(encrypted_data, session_key)
        return data
