from src import file_service
from mock import mock_open
import mock


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

    result = file_service.read("bla")

    assert result is False
    open_mock.assert_not_called()


def test_read_directory(mocker):
    open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data="blabla")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.read("bla")

    assert result is False
    open_mock.assert_not_called()


def test_read_with_dir_name(mocker):
    open_mock = mocker.patch("builtins.open", new_callable=mock_open, read_data="blabla")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.read("bla")

    assert result is False
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

    result = file_service.delete("bla")

    assert result is False
    delete_mock.assert_not_called()


def test_delete_file_with_directory_name(mocker):
    delete_mock = mocker.patch("os.remove")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.delete("bla")

    assert result is False
    delete_mock.assert_not_called()


def test_delete_directory(mocker):
    delete_mock = mocker.patch("os.remove")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.delete("bla")

    assert result is False
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

    result = file_service.change_dir("bla")

    assert result is False
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

    result = file_service.set_permissions("bla", 111)

    assert result is False
    permock.assert_not_called()


def test_set_permissions_directory(mocker):
    permock = mocker.patch("os.chmod")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.set_permissions("bla", 111)

    assert result is False
    permock.assert_not_called()


def test_set_permissions_file_with_dir_name(mocker):
    permock = mocker.patch("os.chmod")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.set_permissions("bla", 111)

    assert result is False
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

    result = file_service.get_permissions("bla")

    assert result is False
    permock.assert_not_called()


def test_get_permissions_directory(mocker):
    permock = mocker.patch("os.stat")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.get_permissions("bla")

    assert result is False
    permock.assert_not_called()


def test_get_permissions_file_with_dir_name(mocker):
    permock = mocker.patch("os.stat")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.get_permissions("bla")

    assert result is False
    permock.assert_not_called()


def test_get_file_metadata_success(mocker):
    permock = mocker.patch("os.stat")
    result_mock = mock.Mock()
    result_mock.st_ctime = 1
    result_mock.st_mtime = 2
    result_mock.st_size = 3
    permock.return_value = result_mock
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = False

    result = file_service.get_file_meta_data("bla")

    assert result == (1, 2, 3)
    permock.assert_called_with("bla")


def test_get_non_existing_file_metadata(mocker):
    permock = mocker.patch("os.stat")
    mocker.patch("os.path.isfile").return_value = False
    mocker.patch("os.path.isdir").return_value = False

    result = file_service.get_file_meta_data("bla")

    assert result is False
    permock.assert_not_called()


def test_get_file_with_dirname_metadata(mocker):
    permock = mocker.patch("os.stat")
    mocker.patch("os.path.isfile").return_value = True
    mocker.patch("os.path.isdir").return_value = True

    result = file_service.get_file_meta_data("bla")

    assert result is False
    permock.assert_not_called()