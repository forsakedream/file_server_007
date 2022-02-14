import pytest
from src.file_service import RawFileService, SignedFileService
from src.crypto import Signature
from mock import mock_open


def test_read_signed_success(mocker):
    signers_labels = {"md5": iter([True, False, False]),
                      "sha512": iter([False, True, False]),
                      "sha256": iter([False, False, True])}
    for signer_label in signers_labels:
        data = "blabla"
        read_data_mock = mocker.patch("src.file_service.raw_file_service.RawFileService.read")
        read_data_mock.return_value = data
        sig_path_mock = mocker.patch("src.crypto.signature.Signature.sig_filename")
        sig_path_mock.return_value = f"bla.{signer_label}"
        os_exists_mock = mocker.patch("os.path.exists")
        os_exists_mock.return_value = True
        signer = Signature().get_signer(signer_label)
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        result = SignedFileService(RawFileService).read("bla")

        assert result == data
        read_data_mock.assert_called_with("bla")
        open_mock.assert_called_with(f"bla.{signer_label}", "r")


def test_read_signed_file_broken(mocker):
    signers_labels = {"md5": iter([True, False, False]),
                      "sha512": iter([False, True, False]),
                      "sha256": iter([False, False, True])}
    for signer_label in signers_labels:
        data = "blabla"
        read_data_mock = mocker.patch("src.file_service.file_service.read")
        read_data_mock.return_value = data
        os_exists_mock = mocker.patch("os.path.exists")
        os_exists_mock.side_effect = signers_labels[signer_label]
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=data)

        with pytest.raises(Exception):
            assert file_service.read_signed("bla")
            read_data_mock.assert_called_with("bla")
            open_mock.assert_not_called()


def test_read_signed_file_is_missing(mocker):
    signers_labels = ["md5", "sha512", "sha256"]

    for _ in signers_labels:
        data = "blabla"
        read_data_mock = mocker.patch("src.file_service.file_service.read")
        read_data_mock.return_value = data
        os_exists_mock = mocker.patch("os.path.exists")
        os_exists_mock.return_value = False
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=data)

        with pytest.raises(Exception):
            assert file_service.read_signed("bla")
            read_data_mock.assert_called_with("bla")
            open_mock.assert_not_called()


def test_read_signed_file_when_other_sig_files_exists(mocker):
    signers_labels = {"md5": iter([False, True, True]),
                      "sha512": iter([True, False, True]),
                      "sha256": iter([True, True, False])}

    for signer_label in signers_labels:
        data = "blabla"
        read_data_mock = mocker.patch("src.file_service.file_service.read")
        read_data_mock.return_value = data
        os_exists_mock = mocker.patch("os.path.exists")
        os_exists_mock.side_effect = signers_labels[signer_label]
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=data)

        with pytest.raises(Exception):
            assert file_service.read_signed("bla")
            read_data_mock.assert_called_with("bla")
            open_mock.assert_not_called()


def test_create_signed_success(mocker):
    create_mock = mocker.patch("src.file_service.file_service.create")
    create_mock.return_value = "bla"
    write_mock = mock_open()
    data = "blabla"
    mocker.patch("builtins.open", write_mock, create=True)
    for _ in ["md5", "sha512", "sha256"]:
        signer = SignatureFactory.get_signer(_)

        filename, sig_filename = file_service.create_signed(data, _)

        assert sig_filename == f"bla.{_}"
        assert filename == "bla"
        write_mock.assert_called_with(f"bla.{_}", "w")
        write_mock().write.assert_called_with(signer(data))
