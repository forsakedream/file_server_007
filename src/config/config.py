import configparser
from src.utils import Singleton


class Config(metaclass=Singleton):
    SIGNATURE_SECTION = "Signature"
    CRYPTO = "Encryption"

    def __init__(self, filename=None):
        self.filename = filename
        self.config_data = None
        if filename:
            self.load(self.filename)

    def load(self, filename):
        self.config_data = configparser.ConfigParser()
        self.config_data.read(filename)

    def get_param(self, section, param, default):
        value = default
        if section in self.config_data:
            if param in self.config_data[section]:
                value = self.config_data[section][param]
        return value

    def is_encrypted(self):
        return self.get_param(Config.CRYPTO, "enabled", "false")

    def is_signed(self):
        return self.get_param(Config.SIGNATURE_SECTION, "enabled", "false")

    def signature_algo(self):
        return self.get_param(Config.SIGNATURE_SECTION, "signature_algo", "md5")

    def key_path(self):
        return self.get_param(Config.CRYPTO, "key_path", ".")

    def sig_path(self):
        return self.get_param(Config.SIGNATURE_SECTION, "sig_path", ".")

    def encryption_type(self):
        return self.get_param(Config.CRYPTO, "encryption_type", "aes")
