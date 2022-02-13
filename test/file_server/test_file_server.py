import pytest
import mock
from src import file_service
from src.crypto import SignatureFactory
from mock import mock_open


def test_list_dir_success_flow(mocker):
    list_dir_mock = mocker.patch("os.listdir")
    list_dir_mock.return_value = ['a', 'b', 'c']

    res = file_service.list_dir()

    list_dir_mock.assert_called_once()
    assert res == ["a", "b", "c"]


def test_create_file_success(mocker):
    open_mock = mock_open()
    mocker.patch("builtins.open", open_mock, create=True)
    mocker.patch("src.utils.generate_name").return_value = "blabla"

    result = file_service.create("bla")

    assert result == "blabla"
    open_mock.assert_called_with("blabla", "w")
    open_mock().write.assert_called_with("bla")


def test_create_file_with_existing_dir_name(mocker):
    open_mock = mock_open()
    mocker.patch("builtins.open", open_mock, create=True)
    generate_name_mock = mocker.patch("src.utils.utils.generate_random")
    mocker.patch("os.path.isfile").side_effect = iter([False, False])
    mocker.patch("os.path.isdir").side_effect = iter([True, False])

    file_service.create("bla")

    assert generate_name_mock.call_count == 2
    open_mock.assert_called_once()


def test_create_file_with_existing_file_name(mocker):
    open_mock = mock_open()
    mocker.patch("builtins.open", open_mock, create=True)
    generate_name_mock = mocker.patch("src.utils.utils.generate_random")
    mocker.patch("os.path.isfile").side_effect = iter([True, False])
    mocker.patch("os.path.isdir").side_effect = iter([False, False])

    file_service.create("bla")

    assert generate_name_mock.call_count == 2
    open_mock.assert_called_once()


def test_create_file_with_existing_name(mocker):
    open_mock = mock_open()
    mocker.patch("builtins.open", open_mock, create=True)
    generate_name_mock = mocker.patch("src.utils.utils.generate_random")
    mocker.patch("os.path.isfile").side_effect = iter([True, False, False])
    mocker.patch("os.path.isdir").side_effect = iter([True, False, False])

    file_service.create("bla")

    assert generate_name_mock.call_count == 3
    open_mock.assert_called_once()


def test_read_file_success(mocker):
    open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data="blabla")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = False

    result = file_service.read("bla")

    assert result == "blabla"
    open_mock.assert_called_with("bla", "r")


def test_read_non_existing_file(mocker):
    open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data="blabla")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = False

    with pytest.raises(ValueError):
        assert file_service.read("bla")
        open_mock.assert_not_called()


def test_read_directory(mocker):
    open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data="blabla")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = True

    with pytest.raises(ValueError):
        assert file_service.read("bla")
        open_mock.assert_not_called()


def test_read_with_dir_name(mocker):
    open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data="blabla")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    with pytest.raises(ValueError):
        assert file_service.read("bla")
        open_mock.assert_not_called()


def test_delete_success(mocker):
    delete_mock = mocker.patch("os.remove")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = False

    result = file_service.delete("bla")

    assert result is True
    delete_mock.assert_called_with("bla")


def test_delete_non_existing_file(mocker):
    delete_mock = mocker.patch("os.remove")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = False

    with pytest.raises(ValueError):
        assert file_service.delete("bla")
        delete_mock.assert_not_called()


def test_delete_file_with_directory_name(mocker):
    delete_mock = mocker.patch("os.remove")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    with pytest.raises(ValueError):
        assert file_service.delete("bla")
        delete_mock.assert_not_called()


def test_delete_directory(mocker):
    delete_mock = mocker.patch("os.remove")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = True

    with pytest.raises(ValueError):
        assert file_service.delete("bla")
        delete_mock.assert_not_called()


def test_cd_success(mocker):
    ch_dir = mocker.patch("os.chdir")
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.change_dir("bla")

    assert result is True
    ch_dir.assert_called_with("bla")


def test_cd_not_existing_directory(mocker):
    ch_dir = mocker.patch("os.chdir")
    mocker.patch("os.path.isdir").return_value = False

    with pytest.raises(ValueError):
        assert file_service.change_dir("bla")
        ch_dir.assert_not_called()


def test_set_permissions_success(mocker):
    permock = mocker.patch("os.chmod")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = False

    result = file_service.set_permissions("bla", 111)

    assert result is True
    permock.assert_called_with("bla", 111)


def test_set_permissions_non_existing_file(mocker):
    permock = mocker.patch("os.chmod")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = False

    with pytest.raises(ValueError):
        assert file_service.set_permissions("bla", 111)
        permock.assert_not_called()


def test_set_permissions_directory(mocker):
    permock = mocker.patch("os.chmod")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = True

    with pytest.raises(ValueError):
        assert file_service.set_permissions("bla", 111)
        permock.assert_not_called()


def test_set_permissions_file_with_dir_name(mocker):
    permock = mocker.patch("os.chmod")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    with pytest.raises(ValueError):
        assert file_service.set_permissions("bla", 111)
        permock.assert_not_called()


def test_get_permissions_success(mocker):
    permock = mocker.patch("os.stat")
    result_mock = mock.Mock()
    result_mock.st_mode = True
    permock.return_value = result_mock
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = False

    result = file_service.get_permissions("bla")

    assert result == oct(True)
    permock.assert_called_with("bla")


def test_get_permissions_non_existing_file(mocker):
    permock = mocker.patch("os.stat")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = False

    with pytest.raises(ValueError):
        assert file_service.get_permissions("bla")
        permock.assert_not_called()


def test_get_permissions_directory(mocker):
    permock = mocker.patch("os.stat")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = True

    with pytest.raises(ValueError):
        assert file_service.get_permissions("bla")
        permock.assert_not_called()


def test_get_permissions_file_with_dir_name(mocker):
    permock = mocker.patch("os.stat")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    with pytest.raises(ValueError):
        assert file_service.get_permissions("bla")
        permock.assert_not_called()


def test_get_file_metadata_success(mocker):
    metadatamock = mocker.patch("os.stat")
    result_mock = mock.Mock()
    result_mock.st_ctime = 1
    result_mock.st_mtime = 2
    result_mock.st_size = 3
    metadatamock.return_value = result_mock
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = False

    result = file_service.get_file_meta_data("bla")

    assert result == (file_service.file_service._to_dt(1),
                      file_service.file_service._to_dt(2),
                      3)
    metadatamock.assert_called_with("bla")


def test_get_non_existing_file_metadata(mocker):
    metadatamock = mocker.patch("os.stat")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = False

    with pytest.raises(ValueError):
        assert file_service.get_file_meta_data("bla")
        metadatamock.assert_not_called()


def test_get_file_with_dirname_metadata(mocker):
    metadatamock = mocker.patch("os.stat")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    with pytest.raises(ValueError):
        assert file_service.get_file_meta_data("bla")
        metadatamock.assert_not_called()


def test_read_signed_success(mocker):
    signers_labels = {"md5": iter([True, False, False]),
                      "sha512": iter([False, True, False]),
                      "sha256": iter([False, False, True])}
    for signer_label in signers_labels:
        data = "blabla"
        read_data_mock = mocker.patch("src.file_service.file_service.read")
        read_data_mock.return_value = data
        os_exists_mock = mocker.patch("os.path.exists")
        os_exists_mock.side_effect = signers_labels[signer_label]
        signer = SignatureFactory.get_signer(signer_label)
        open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data=signer(data))

        result = file_service.read_signed("bla")

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
