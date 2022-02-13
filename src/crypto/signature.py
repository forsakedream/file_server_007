import hashlib
from typing import Dict


class SignatureFactory(type):
    signers: Dict = {}

    def __new__(cls, classname, parents, attributes):
        if "__call__" not in attributes:
            raise Exception(f"Signer class must implement {classname}.__call__ function")
        signer_class = type(classname, parents, attributes)
        if "label" not in attributes:
            signer_class.label = classname.lower()
        SignatureFactory.signers[signer_class.label] = signer_class()
        return signer_class

    @staticmethod
    def get_signer(label):
        return SignatureFactory.signers[label]


class Signature:
    label = ""

    def sig_filename(self, filename):
        return f"{filename}.{type(self).label}"


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
