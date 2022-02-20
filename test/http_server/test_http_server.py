import json
import pytest
from src.http_server import create_web_app
from src.user_service import UserService


@pytest.fixture()
async def client_server_with_raw_file_service(client_server, raw_file_service):
    client, server = client_server
    uuid = UserService().add_session("test", "test")
    headers = {'Authorization': str(uuid)}
    return client, raw_file_service, headers


@pytest.fixture()
async def client_server_with_signed_file_service(client_server, signed_file_service):
    client, server = client_server
    uuid = UserService().add_session("test", "test")
    headers = {'Authorization': str(uuid)}
    return client, signed_file_service, headers


@pytest.fixture()
async def client_server_with_encrypted_file_service(client_server, encrypted_file_service):
    client, server = client_server
    uuid = UserService().add_session("test", "test")
    headers = {'Authorization': str(uuid)}
    return client, encrypted_file_service, headers


@pytest.fixture()
async def client_server_with_encrypted_and_signed_file_service(client_server, encrypted_and_signed_file_service):
    client, server = client_server
    uuid = UserService().add_session("test", "test")
    headers = {'Authorization': str(uuid)}
    return client, encrypted_and_signed_file_service, headers


@pytest.fixture()
async def client_server(aiohttp_client, tmpdir):
    server = create_web_app(str(tmpdir))
    client = await aiohttp_client(server)
    return client, server


@pytest.fixture()
def raw_file_service(mocker):
    config = mocker.patch("src.config.Config")
    config.is_signed.return_value = False
    config.is_encrypted.return_value = False
    return config


@pytest.fixture()
def signed_file_service(mocker):
    config = mocker.patch("src.config.Config")
    config.is_signed.return_value = True
    config.is_encrypted.return_value = False
    return config


@pytest.fixture()
def encrypted_file_service(mocker):
    config = mocker.patch("src.config.Config")
    config.is_signed.return_value = False
    config.is_encrypted.return_value = True
    return config


@pytest.fixture()
def encrypted_and_signed_file_service(mocker):
    config = mocker.patch("src.config.Config")
    config.is_signed.return_value = True
    config.is_encrypted.return_value = True
    return config


async def test_login_success(client_server):
    client, _ = client_server
    responce = await client.post('/login', data=b'{"username":"test", "password":"test"}')
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "Authorization" in data
    assert len(data["Authorization"]) == 36

    UserService().logout(data["Authorization"])


async def test_incorrect_login(client_server):
    client, _ = client_server
    responce = await client.post('/login', data=b'{"username":"fake", "password":"pass"}')
    assert responce.status == 404


async def test_incorrect_login_incorrect_body(client_server):
    client, _ = client_server
    responce = await client.post('/login', data=b'{"username":"fake", "password":"pass"')
    assert responce.status == 500


async def test_sign_up_success(client_server):
    client, _ = client_server
    responce = await client.post('/sign_up', data=b'{"username":"test1", "password":"test1"}')
    assert responce.status == 200

    UserService().delete_user("test1")


async def test_incorrect_sign_up(client_server):
    client, _ = client_server
    responce = await client.post('/sign_up', data=b'{"username":"test", "password":"test"}')
    assert responce.status == 406


async def test_incorrect_sign_up_with_incorrect_body(client_server):
    client, _ = client_server
    responce = await client.post('/sign_up', data=b'{"username":"test", "password":"te}')
    assert responce.status == 500


async def test_logout_success(client_server):
    client, _ = client_server
    uuid = UserService().add_session("test", "test")
    responce = await client.post('/logout', headers={'Authorization': str(uuid)})
    assert responce.status == 200


async def test_incorrect_logout(client_server):
    client, _ = client_server
    responce = await client.post('/logout', headers={'Authorization': "uuid"})
    assert responce.status == 400


async def test_raw_check_ls(client_server_with_raw_file_service, tmpdir):
    client, _, headers = client_server_with_raw_file_service
    responce = await client.get("/ls", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    assert type(json.loads(data)) == list


async def test_raw_check_pwd(client_server_with_raw_file_service, tmpdir):
    client, _ , headers = client_server_with_raw_file_service
    responce = await client.get("/pwd", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "working_directory" in data
    assert data["working_directory"] == str(tmpdir)


async def test_raw_check_write(client_server_with_raw_file_service, tmpdir):
    client, _, headers = client_server_with_raw_file_service
    responce = await client.post('/write', data=b'test data', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "created_file" in data
    assert len(data["created_file"]) == 10


async def test_raw_read_file(client_server_with_raw_file_service, tmpdir):
    test_file = tmpdir / "test_file"
    with test_file.open("w") as f:
        f.write("data")
    client, _, headers = client_server_with_raw_file_service
    responce = await client.get(f'/read?filename={str(test_file)}', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "file_content" in data
    assert data["file_content"] == "data"


async def test_raw_read_metadata(client_server_with_raw_file_service, tmpdir):
    test_file = tmpdir / "test_file"
    with test_file.open("w") as f:
        f.write("data")
    client, _, headers = client_server_with_raw_file_service
    responce = await client.get(f'/read_meta?filename={str(test_file)}', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "creation_date" in data
    assert "modification_date" in data
    assert "file_size" in data


async def test_raw_cd(client_server_with_raw_file_service, tmpdir):
    p = tmpdir.mkdir("test_dir")
    client, _, headers = client_server_with_raw_file_service
    responce = await client.put(f"/cd?dir={str(p)}", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    assert data == str(True)


async def test_encrypted_check_ls(client_server_with_encrypted_file_service, tmpdir):
    client, _, headers = client_server_with_encrypted_file_service
    responce = await client.get("/ls", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    assert type(json.loads(data)) == list


async def test_encrypted_check_pwd(client_server_with_encrypted_file_service, tmpdir):
    client, _ , headers = client_server_with_encrypted_file_service
    responce = await client.get("/pwd", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "working_directory" in data
    assert data["working_directory"] == str(tmpdir)


async def test_encrypted_check_write(client_server_with_encrypted_file_service, tmpdir):
    client, _, headers = client_server_with_encrypted_file_service
    responce = await client.post('/write', data=b'test data', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "created_file" in data
    assert len(data["created_file"]) == 10


async def test_encrypted_read_file(client_server_with_encrypted_file_service, tmpdir):
    test_file = tmpdir / "test_file"
    with test_file.open("w") as f:
        f.write("data")
    client, _, headers = client_server_with_encrypted_file_service
    responce = await client.get(f'/read?filename={str(test_file)}', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "file_content" in data
    assert data["file_content"] == "data"


async def test_encrypted_read_metadata(client_server_with_encrypted_file_service, tmpdir):
    test_file = tmpdir / "test_file"
    with test_file.open("w") as f:
        f.write("data")
    client, _, headers = client_server_with_encrypted_file_service
    responce = await client.get(f'/read_meta?filename={str(test_file)}', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "creation_date" in data
    assert "modification_date" in data
    assert "file_size" in data


async def test_encrypted_cd(client_server_with_encrypted_file_service, tmpdir):
    p = tmpdir.mkdir("test_dir")
    client, _, headers = client_server_with_encrypted_file_service
    responce = await client.put(f"/cd?dir={str(p)}", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    assert data == str(True)


async def test_signed_check_ls(client_server_with_signed_file_service, tmpdir):
    client, _, headers = client_server_with_signed_file_service
    responce = await client.get("/ls", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    assert type(json.loads(data)) == list


async def test_signed_check_pwd(client_server_with_signed_file_service, tmpdir):
    client, _ , headers = client_server_with_signed_file_service
    responce = await client.get("/pwd", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "working_directory" in data
    assert data["working_directory"] == str(tmpdir)


async def test_signed_check_write(client_server_with_signed_file_service, tmpdir):
    client, _, headers = client_server_with_signed_file_service
    responce = await client.post('/write', data=b'test data', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "created_file" in data
    assert len(data["created_file"]) == 10


async def test_signed_read_file(client_server_with_signed_file_service, tmpdir):
    test_file = tmpdir / "test_file"
    with test_file.open("w") as f:
        f.write("data")
    client, _, headers = client_server_with_signed_file_service
    responce = await client.get(f'/read?filename={str(test_file)}', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "file_content" in data
    assert data["file_content"] == "data"


async def test_signed_read_metadata(client_server_with_signed_file_service, tmpdir):
    test_file = tmpdir / "test_file"
    with test_file.open("w") as f:
        f.write("data")
    client, _, headers = client_server_with_signed_file_service
    responce = await client.get(f'/read_meta?filename={str(test_file)}', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "creation_date" in data
    assert "modification_date" in data
    assert "file_size" in data


async def test_signed_cd(client_server_with_signed_file_service, tmpdir):
    p = tmpdir.mkdir("test_dir")
    client, _, headers = client_server_with_signed_file_service
    responce = await client.put(f"/cd?dir={str(p)}", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    assert data == str(True)


async def test_signed_and_encrypted_check_ls(client_server_with_encrypted_and_signed_file_service, tmpdir):
    client, _, headers = client_server_with_encrypted_and_signed_file_service
    responce = await client.get("/ls", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    assert type(json.loads(data)) == list


async def test_signed_and_encrypted_check_pwd(client_server_with_encrypted_and_signed_file_service, tmpdir):
    client, _ , headers = client_server_with_encrypted_and_signed_file_service
    responce = await client.get("/pwd", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "working_directory" in data
    assert data["working_directory"] == str(tmpdir)


async def test_signed_and_encrypted_check_write(client_server_with_encrypted_and_signed_file_service, tmpdir):
    client, _, headers = client_server_with_encrypted_and_signed_file_service
    responce = await client.post('/write', data=b'test data', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "created_file" in data
    assert len(data["created_file"]) == 10


async def test_encrypted_and_signed_read_file(client_server_with_encrypted_and_signed_file_service, tmpdir):
    test_file = tmpdir / "test_file"
    with test_file.open("w") as f:
        f.write("data")
    client, _, headers = client_server_with_encrypted_and_signed_file_service
    responce = await client.get(f'/read?filename={str(test_file)}', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "file_content" in data
    assert data["file_content"] == "data"


async def test_encrypted_and_signed_read_metadata(client_server_with_encrypted_and_signed_file_service, tmpdir):
    test_file = tmpdir / "test_file"
    with test_file.open("w") as f:
        f.write("data")
    client, _, headers = client_server_with_encrypted_and_signed_file_service
    responce = await client.get(f'/read_meta?filename={str(test_file)}', headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    data = json.loads(data)
    assert "creation_date" in data
    assert "modification_date" in data
    assert "file_size" in data


async def test_encrypted_and_signed_cd(client_server_with_encrypted_and_signed_file_service, tmpdir):
    p = tmpdir.mkdir("test_dir")
    client, _, headers = client_server_with_encrypted_and_signed_file_service
    responce = await client.put(f"/cd?dir={str(p)}", headers=headers)
    assert responce.status == 200
    data = b''
    while not responce.content.at_eof():
        data += await responce.content.read()
    data = data.decode()
    assert data == str(True)


async def test_unauth_ls(client_server):
    client, _ = client_server
    responce = await client.get("/ls")
    assert responce.status == 401


async def test_unauth_pwd(client_server):
    client, _ = client_server
    responce = await client.get("/pwd")
    assert responce.status == 401


async def test_unauth_write(client_server):
    client, _ = client_server
    responce = await client.post('/write', data=b'test data')
    assert responce.status == 401


async def test_unauth_file(client_server):
    client, _ = client_server
    responce = await client.get(f'/read?filename=test')
    assert responce.status == 401


async def test_unauth_read_metadata(client_server):
    client, _ = client_server
    responce = await client.get(f'/read_meta?filename=test')
    assert responce.status == 401


async def test_unauth_cd(client_server):
    client, _ = client_server
    responce = await client.put(f"/cd?dir=test")
    assert responce.status == 401

