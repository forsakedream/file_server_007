import pytest
import os
from src.file_service import RawFileService, SignedFileService
from src.crypto import Signature
from mock import mock_open


def test_read_signed_success(mocker):
    signers_labels = {"md5": iter([True, False, False]),
                      "sha512": iter([False, True, False]),
                      "sha256": iter([False, False, True])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    read_data_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.read")
    read_data_mock.return_value = data
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    for label in signers_labels:
        signer = Signature().get_signer_by_label(label)
        os_exists_mock.side_effect = signers_labels[label]
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        result = SignedFileService(RawFileService).read("bla")

        assert result == data
        read_data_mock.assert_called_with(filename)
        open_mock.assert_called_with(os.path.join(".", f"{filename}.{label}"), "r")


def test_read_signed_file_broken(mocker):
    signers_labels = {"md5": iter([True, False, False]),
                      "sha512": iter([False, True, False]),
                      "sha256": iter([False, False, True])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    read_data_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.read")
    read_data_mock.return_value = data
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    for label in signers_labels:
        os_exists_mock.side_effect = signers_labels[label]
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=data)

        with pytest.raises(Exception):
            assert SignedFileService(RawFileService).read("bla")

        read_data_mock.assert_called_with(filename)
        open_mock.assert_called_with(os.path.join(".", f"{filename}.{label}"), "r")


def test_read_signed_file_is_missing(mocker):
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    read_data_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.read")
    read_data_mock.return_value = data
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    for label in ("md5", "sha512", "sha256"):
        os_exists_mock.return_value = False
        signer = Signature().get_signer_by_label(label)
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        with pytest.raises(Exception):
            assert SignedFileService(RawFileService).read("bla")

        read_data_mock.assert_called_with(filename)
        open_mock.assert_not_called()


def test_read_signed_file_when_all_sig_files_exists(mocker):
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    read_data_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.read")
    read_data_mock.return_value = data
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    for label in ("md5", "sha512", "sha256"):
        os_exists_mock.return_value = True
        signer = Signature().get_signer_by_label(label)
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        with pytest.raises(Exception):
            assert SignedFileService(RawFileService).read("bla")

        read_data_mock.assert_called_with(filename)
        open_mock.assert_not_called()


def test_read_signed_file_when_other_sig_files_exists(mocker):
    signers_labels = {"md5": iter([False, True, False]),
                      "sha512": iter([True, False, False]),
                      "sha256": iter([True, False, False])}
    os_exists_mock = mocker.patch("os.path.exists")
    data = "blabla"
    filename = "bla"
    read_data_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.read")
    read_data_mock.return_value = data
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    for label in signers_labels:
        os_exists_mock.side_effect = signers_labels[label]
        signer = Signature().get_signer_by_label(label)
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        with pytest.raises(Exception):
            assert SignedFileService(RawFileService).read("bla")

        read_data_mock.assert_called_with(filename)
        open_mock.assert_called_once()


def test_create_signed_success(mocker):
    data = "blabla"
    filename = "bla"
    open_mock = mock_open()
    create_data_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.create")
    create_data_mock.return_value = filename
    algo_mock = mocker.patch("src.config.Config.get_algo")
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    for label in ("md5", "sha512", "sha256"):
        signer = Signature().get_signer_by_label(label)
        algo_mock.return_value = label
        mocker.patch("builtins.open", open_mock, create=True)

        result1, result2 = SignedFileService(RawFileService).create(data)

        assert result1 == filename
        assert result2 == os.path.join(".", f"{filename}.{label}")
        open_mock.assert_called_with(os.path.join(".", f"{filename}.{label}"), "w")
        open_mock().write.assert_called_with(signer(data))
        create_data_mock.assert_called_with(data)


def test_remove_success(mocker):
    signers_labels = {"md5": iter([True, False, False]),
                      "sha512": iter([False, True, False]),
                      "sha256": iter([False, False, True])}
    remove_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.remove")
    remove_mock.return_value = True
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in signers_labels:
        os_exists_mock.side_effect = signers_labels[label]

        SignedFileService(RawFileService).remove(filename)

        remove_mock.assert_any_call(filename)
        remove_mock.assert_any_call(os.path.join(".", f"{filename}.{label}"))


def test_remove_sig_file_doesnt_exists(mocker):
    remove_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.remove")
    remove_mock.return_value = True
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in ("md5", "sha512", "sha256"):
        os_exists_mock.return_value = False

        with pytest.raises(Exception):
            SignedFileService(RawFileService).remove(filename)

        remove_mock.assert_called_with(filename)


def test_remove_other_sig_file_exists(mocker):
    signers_labels = {"md5": iter([False, True, False]),
                      "sha512": iter([True, False, False]),
                      "sha256": iter([True, False, False])}
    remove_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.remove")
    remove_mock.return_value = True
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in signers_labels:
        os_exists_mock.side_effect = signers_labels[label]

        SignedFileService(RawFileService).remove(filename)

        remove_mock.assert_any_call(filename)


def test_remove_when_all_sig_files_exists(mocker):
    remove_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.remove")
    remove_mock.return_value = True
    sig_path_mock = mocker.patch("src.config.Config.sig_path")
    sig_path_mock.return_value = "."
    os_exists_mock = mocker.patch("os.path.exists")
    filename = "bla"
    for label in ("md5", "sha512", "sha256"):
        os_exists_mock.return_value = True

        with pytest.raises(Exception):
            SignedFileService(RawFileService).remove(filename)

        remove_mock.assert_called_with(filename)