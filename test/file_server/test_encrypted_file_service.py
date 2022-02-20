import mock
import pytest
import os

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from src.file_service import EncryptedFileService
from src.crypto import Encryption
from mock import mock_open
from Crypto import Random


@pytest.fixture()
def file_service_mock():
    file_service_mock = mock.Mock()
    file_service_mock.workdir = "."
    return file_service_mock


@pytest.fixture()
def key_path_mock(mocker):
    key_path_mock = mocker.patch("src.config.Config.key_path")
    key_path_mock.return_value = "."
    return key_path_mock


@pytest.fixture()
def rsa_key_mock(mocker):
    rsa_key_mock = mocker.patch("src.crypto.encryption.HybridEncryption.rsa_key")
    rsa_key = PKCS1_OAEP.new(RSA.generate(1024, Random.new().read))
    rsa_key_mock.encrypt = rsa_key.encrypt
    rsa_key_mock.decrypt = rsa_key.decrypt
    return rsa_key


def test_read_encrypted_success(file_service_mock, key_path_mock, rsa_key_mock, mocker):
    encryptors_labels = {"aes": iter([True, False]),
                         "hybrid": iter([False, True])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    for _ in encryptors_labels:
        filename = f"bla"
        encryptor = Encryption.get_encryptor_by_label(_)
        os_exists_mock.side_effect = encryptors_labels[_]
        encrypted_data, key = encryptor.encrypt(data)
        open_mock = mocker.patch('builtins.open', new_callable=mock_open, read_data=bytes(key))
        handlers = (open_mock.return_value, mock_open(read_data=bytes(encrypted_data)).return_value,)
        open_mock.side_effect = handlers

        result = EncryptedFileService(file_service_mock).read(filename)

        assert data == result
        open_mock.assert_any_call(os.path.join(".", f"{filename}.{_}"), "rb")
        open_mock.assert_any_call(filename, "rb")


def test_read_key_file_broken(file_service_mock, key_path_mock, rsa_key_mock, mocker):
    encryptors_labels = {"aes": iter([True, False]),
                         "hybrid": iter([False, True])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    for _ in encryptors_labels:
        filename = f"bla"
        encryptor = Encryption.get_encryptor_by_label(_)
        os_exists_mock.side_effect = encryptors_labels[_]
        encrypted_data, key = encryptor.encrypt(data)
        open_mock = mocker.patch('builtins.open', new_callable=mock_open, read_data=data)
        handlers = (open_mock.return_value, mock_open(read_data=bytes(encrypted_data)).return_value,)
        open_mock.side_effect = handlers

        with pytest.raises(Exception):
            EncryptedFileService(file_service_mock).read(filename)

        open_mock.assert_any_call(os.path.join(".", f"{filename}.{_}"), "rb")
        open_mock.assert_any_call(filename, "rb")


def test_read_encrypted_data_file_broken(file_service_mock, key_path_mock, rsa_key_mock, mocker):
    encryptors_labels = {"aes": iter([True, False]),
                         "hybrid": iter([False, True])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    for _ in encryptors_labels:
        filename = f"bla"
        encryptor = Encryption.get_encryptor_by_label(_)
        os_exists_mock.side_effect = encryptors_labels[_]
        encrypted_data, key = encryptor.encrypt(data)
        open_mock = mocker.patch('builtins.open', new_callable=mock_open, read_data=bytes(key))
        handlers = (open_mock.return_value, mock_open(read_data=data).return_value,)
        open_mock.side_effect = handlers

        with pytest.raises(Exception):
            EncryptedFileService(file_service_mock).read(filename)

        open_mock.assert_any_call(os.path.join(".", f"{filename}.{_}"), "rb")
        open_mock.assert_any_call(filename, "rb")


def test_read_key_file_is_missing(file_service_mock, key_path_mock, rsa_key_mock, mocker):
    encryptors_labels = {"aes": iter([False, True]),
                         "hybrid": iter([True, False])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    for _ in encryptors_labels:
        filename = f"bla"
        encryptor = Encryption.get_encryptor_by_label(_)
        os_exists_mock.side_effect = encryptors_labels[_]
        encrypted_data, key = encryptor.encrypt(data)
        open_mock = mocker.patch('builtins.open', new_callable=mock_open, read_data=bytes(key))
        handlers = (open_mock.return_value, mock_open(read_data=bytes(encrypted_data)).return_value,)
        open_mock.side_effect = handlers

        with pytest.raises(Exception):
            EncryptedFileService(file_service_mock).read(filename)

        open_mock.assert_any_call(filename, "rb")


def test_read_encrypted_file_when_all_key_files_exists(file_service_mock, key_path_mock, rsa_key_mock, mocker):
    encryptors_labels = {"aes": iter([False, True]),
                         "hybrid": iter([True, False])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    for _ in encryptors_labels:
        filename = f"bla"
        encryptor = Encryption.get_encryptor_by_label(_)
        os_exists_mock.return_value = True
        encrypted_data, key = encryptor.encrypt(data)
        open_mock = mocker.patch('builtins.open', new_callable=mock_open, read_data=bytes(key))
        handlers = (open_mock.return_value, mock_open(read_data=bytes(encrypted_data)).return_value,)
        open_mock.side_effect = handlers

        with pytest.raises(Exception):
            EncryptedFileService(file_service_mock).read(filename)

        open_mock.assert_not_called()


def test_read_signed_file_when_other_sig_files_exists(file_service_mock, key_path_mock, rsa_key_mock, mocker):
    encryptors_labels = {"aes": iter([False, True]),
                         "hybrid": iter([True, False])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    for _ in encryptors_labels:
        filename = f"bla"
        encryptor = Encryption.get_encryptor_by_label(_)
        os_exists_mock.return_value = True
        encrypted_data, key = encryptor.encrypt(data)
        open_mock = mocker.patch('builtins.open', new_callable=mock_open, read_data=bytes(key))
        handlers = (open_mock.return_value, mock_open(read_data=bytes(encrypted_data)).return_value,)
        open_mock.side_effect = handlers

        with pytest.raises(Exception):
            EncryptedFileService(file_service_mock).read(filename)

        open_mock.assert_not_called()


def test_read_encrypted_file_when_pem_key_is_broken(file_service_mock, key_path_mock, mocker):
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    rsa_key_mock = mocker.patch("src.crypto.encryption.HybridEncryption.rsa_key")
    rsa_key = PKCS1_OAEP.new(RSA.generate(1025, Random.new().read))
    rsa_key_mock.encrypt = rsa_key.encrypt
    rsa_key_mock.decrypt = rsa_key.decrypt
    filename = f"bla"
    encryptor = Encryption.get_encryptor_by_label("hybrid")
    os_exists_mock.side_effect = iter([False, True])
    encrypted_data, key = encryptor.encrypt(data)
    open_mock = mocker.patch('builtins.open', new_callable=mock_open, read_data=data)
    handlers = (open_mock.return_value, mock_open(read_data=bytes(encrypted_data)).return_value,)
    open_mock.side_effect = handlers

    with pytest.raises(Exception):
        EncryptedFileService(file_service_mock).read(filename)

    open_mock.assert_any_call(os.path.join(".", f"{filename}.hybrid"), "rb")
    open_mock.assert_any_call(filename, "rb")


def test_create_encrypted_success(file_service_mock, key_path_mock, mocker):
    data = "blabla"
    filename = "bla"
    open_mock = mock_open()
    encryption_type_mock = mocker.patch("src.config.Config.encryption_type")
    generate_name_mock = mocker.patch("src.utils.generate_name")
    generate_name_mock.return_value = filename
    for label in ("aes", "hybrid"):
        encryption_type_mock.return_value = label
        mocker.patch("builtins.open", open_mock, create=True)

        result = EncryptedFileService(file_service_mock).create(data)

        assert result == filename
        open_mock.assert_any_call(filename, "wb")
        open_mock.assert_called_with(os.path.join(".", f"{filename}.{label}"), "wb")


def test_remove_success(file_service_mock, key_path_mock, mocker):
    encryptors_labels = {"aes": iter([True, False]),
                         "hybrid": iter([False, True])}
    file_service_mock.remove.return_value = True
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in encryptors_labels:
        os_exists_mock.side_effect = encryptors_labels[label]

        EncryptedFileService(file_service_mock).remove(filename)

        file_service_mock.remove.assert_any_call(filename)
        file_service_mock.remove.assert_any_call(os.path.join(".", f"{filename}.{label}"))


def test_remove_key_file_doesnt_exists(file_service_mock, key_path_mock, mocker):
    file_service_mock.remove.return_value = True
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in ("aes", "hybrid"):
        os_exists_mock.return_value = False

        with pytest.raises(Exception):
            EncryptedFileService(file_service_mock).remove(filename)

        file_service_mock.remove.assert_called_with(filename)


def test_remove_other_key_file_exists(file_service_mock, key_path_mock, mocker):
    encryptors_labels = {"aes": iter([True, False]),
                         "hybrid": iter([False, True])}
    file_service_mock.remove.return_value = True
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in encryptors_labels:
        os_exists_mock.side_effect = encryptors_labels[label]

        EncryptedFileService(file_service_mock).remove(filename)

        file_service_mock.remove.assert_any_call(filename)


def test_remove_when_all_key_files_exists(file_service_mock, key_path_mock, mocker):
    file_service_mock.remove.return_value = True
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in ("aes", "hybrid"):
        os_exists_mock.return_value = True

        with pytest.raises(Exception):
            EncryptedFileService(file_service_mock).remove(filename)

        file_service_mock.remove.assert_called_with(filename)
