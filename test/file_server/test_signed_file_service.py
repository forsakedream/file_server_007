import mock
import pytest
import os
from src.file_service import SignedFileService
from src.crypto import Signature
from mock import mock_open


@pytest.fixture()
def file_service():
    file_service_mock = mock.Mock()
    file_service_mock.workdir = "."
    return file_service_mock


@pytest.fixture()
def sig_path_mock(mocker):
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    return sig_path_mock


def test_read_signed_success(file_service, sig_path_mock, mocker):
    signers_labels = {"md5": iter([True, False, False]),
                      "sha512": iter([False, True, False]),
                      "sha256": iter([False, False, True])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    file_service.read.return_value = data
    for label in signers_labels:
        signer = Signature().get_signer_by_label(label)
        os_exists_mock.side_effect = signers_labels[label]
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        result = SignedFileService(file_service).read("bla")

        assert result == data
        file_service.read.assert_called_with(filename)
        open_mock.assert_called_with(os.path.join(".", f"{filename}.{label}"), "r")


def test_read_signed_file_broken(file_service, sig_path_mock, mocker):
    signers_labels = {"md5": iter([True, False, False]),
                      "sha512": iter([False, True, False]),
                      "sha256": iter([False, False, True])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    file_service.read.return_value = data

    for label in signers_labels:
        os_exists_mock.side_effect = signers_labels[label]
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=data)

        with pytest.raises(Exception):
            assert SignedFileService(file_service).read("bla")

        file_service.read.assert_called_with(filename)
        open_mock.assert_called_with(os.path.join(".", f"{filename}.{label}"), "r")


def test_read_signed_file_is_missing(file_service, sig_path_mock, mocker):
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    file_service.read.return_value = data
    for label in ("md5", "sha512", "sha256"):
        os_exists_mock.return_value = False
        signer = Signature().get_signer_by_label(label)
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        with pytest.raises(Exception):
            assert SignedFileService(file_service).read("bla")

        file_service.read.assert_called_with(filename)
        open_mock.assert_not_called()


def test_read_signed_file_when_all_sig_files_exists(file_service, sig_path_mock, mocker):
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    file_service.read.return_value = data
    for label in ("md5", "sha512", "sha256"):
        os_exists_mock.return_value = True
        signer = Signature().get_signer_by_label(label)
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        with pytest.raises(Exception):
            assert SignedFileService(file_service).read("bla")

        file_service.read.assert_called_with(filename)
        open_mock.assert_not_called()


def test_read_signed_file_when_other_sig_files_exists(file_service, sig_path_mock, mocker):
    signers_labels = {"md5": iter([False, True, False]),
                      "sha512": iter([True, False, False]),
                      "sha256": iter([True, False, False])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    file_service.read.return_value = data
    for label in signers_labels:
        os_exists_mock.side_effect = signers_labels[label]
        signer = Signature().get_signer_by_label(label)
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        with pytest.raises(Exception):
            assert SignedFileService(file_service).read("bla")

        file_service.read.assert_called_with(filename)
        open_mock.assert_called_once()


def test_create_signed_success(file_service, sig_path_mock, mocker):
    data = "blabla"
    filename = "bla"
    open_mock = mock_open()
    file_service.create.return_value = filename
    algo_mock = mocker.patch("src.config.Config.signature_algo")
    for label in ("md5", "sha512", "sha256"):
        signer = Signature().get_signer_by_label(label)
        algo_mock.return_value = label
        mocker.patch("builtins.open", open_mock, create=True)

        result = SignedFileService(file_service).create(data)

        assert result == filename
        open_mock.assert_called_with(os.path.join(".", f"{filename}.{label}"), "w")
        open_mock().write.assert_called_with(signer(data))
        file_service.create.assert_called_with(data)


def test_remove_success(file_service, sig_path_mock, mocker):
    signers_labels = {"md5": iter([True, False, False]),
                      "sha512": iter([False, True, False]),
                      "sha256": iter([False, False, True])}
    file_service.remove.return_value = True
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in signers_labels:
        os_exists_mock.side_effect = signers_labels[label]

        SignedFileService(file_service).remove(filename)

        file_service.remove.assert_any_call(filename)
        file_service.remove.assert_any_call(os.path.join(".", f"{filename}.{label}"))


def test_remove_sig_file_doesnt_exists(file_service, sig_path_mock, mocker):
    file_service.remove.return_value = True
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in ("md5", "sha512", "sha256"):
        os_exists_mock.return_value = False

        with pytest.raises(Exception):
            SignedFileService(file_service).remove(filename)

        file_service.remove.assert_called_with(filename)


def test_remove_other_sig_file_exists(file_service, sig_path_mock,mocker):
    signers_labels = {"md5": iter([False, True, False]),
                      "sha512": iter([True, False, False]),
                      "sha256": iter([True, False, False])}
    file_service.remove.return_value = True
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in signers_labels:
        os_exists_mock.side_effect = signers_labels[label]

        SignedFileService(file_service).remove(filename)

        file_service.remove.assert_any_call(filename)


def test_remove_when_all_sig_files_exists(file_service, sig_path_mock, mocker):
    file_service.remove.return_value = True
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in ("md5", "sha512", "sha256"):
        os_exists_mock.return_value = True

        with pytest.raises(Exception):
            SignedFileService(file_service).remove(filename)

        file_service.remove.assert_called_with(filename)
