import configparser
from src.utils import Singleton


class Config(metaclass=Singleton):
    SIGNATURE_SECTION = "Signature"

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

    def get_algo(self):
        return self.get_param(Config.SIGNATURE_SECTION, "signature_algo", "md5")
