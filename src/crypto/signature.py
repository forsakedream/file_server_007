import hashlib
import os
from src.config import Config


class SignatureFactory(type):

    def __new__(mcs, classname, parents, attributes):
        if "__call__" not in attributes:
            raise Exception(f"Signer class must implement {classname}.__call__ function")
        signer_class = type(classname, parents, attributes)
        if "label" not in attributes:
            signer_class.label = classname.lower()
        return signer_class


class Signature:
    label = ""

    @staticmethod
    def get_signer(filename):
        current_signer = None
        for signer in Signature.__subclasses__():
            if os.path.exists(signer().sig_filename(filename)):
                if not current_signer:
                    current_signer = signer()
                else:
                    raise Exception("More than one signer is found!")
        if current_signer:
            return current_signer
        else:
            raise Exception("Signer is not found!")

    def get_default_signer(self):
        algo = Config().get_algo()
        return self.get_signer_by_label(algo)

    @staticmethod
    def get_signer_by_label(label):
        for signer in Signature.__subclasses__():
            if signer().label == label:
                return signer()

    def sig_filename(self, filename):
        sig_path = Config().sig_path()
        return os.path.join(sig_path, f"{filename}.{type(self).label}")


class MD5Signature(Signature, metaclass=SignatureFactory):
    label = "md5"

    def __call__(self, data):
        return hashlib.md5(data.encode()).hexdigest()


class Sha512Signer(Signature, metaclass=SignatureFactory):
    label = "sha512"

    def __call__(self, data):
        return hashlib.sha512(data.encode()).hexdigest()


class Sha256Signer(Signature, metaclass=SignatureFactory):
    label = "sha256"

    def __call__(self, data):
        return hashlib.sha256(data.encode()).hexdigest()
