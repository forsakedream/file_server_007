from src import file_service
from mock import mock_open


def test_list_dir_success_flow(mocker):
    list_dir_mock = mocker.patch("os.listdir")
    list_dir_mock.return_value = ['a', 'b', 'c']
    res = file_service.list_dir()
    list_dir_mock.assert_called_once()
    assert res == ['a', 'b', 'c']


def test_create_file_success(mocker):
    mocked_open = mock_open()
    mocker.patch("builtins.open", mocked_open, create=True)
    mocker.patch("src.utils.generate_name").return_value = "blabla"

    file_service.create("blabla", "bla")

    mocked_open.assert_called_with("blabla", "w")
    mocked_open().write.assert_called_with("bla")


def test_create_file_dublicate(mocker):
    mocked_open = mock_open()
    mocker.patch("builtins.open", mocked_open, create=True)




def test_delete(mocker):
    delete_mock = mocker.patch("os.remove")
    file_service.delete('bla')
    delete_mock.assert_called_with('bla')


def test_chdir(mocker):
    ch_dir = mocker.patch("os.chdir")
    file_service.change_dir('bla')
    ch_dir.assert_called_with('bla')


def test_set_permissions(mocker):
    permock = mocker.patch("os.chmod")
    file_service.set_permissions('bla', 'blabla')
    permock.assert_called_with('bla', 'blabla')



def test_get_permissions(mocker):
    pass