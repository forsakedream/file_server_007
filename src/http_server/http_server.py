from aiohttp import web
from src.config import Config
from src.user_service import UserService
from src.file_service import RawFileService, SignedFileService, EncryptedFileService
import json


def authorize(func):
    async def wrapped(self, request, *args, **kwargs):
        user_service = self.user_service
        try:
            uuid = request.headers['Authorization']
            user_service.check_authorization(uuid)
            response = await func(self, request, *args, **kwargs)
        except (KeyError, ValueError) as e:
            response = web.Response(status=401, text=str(e))
        except Exception as e:
            response = web.Response(status=500, text=str(e))
        return response
    return wrapped


class Handler:

    def __init__(self, directory):
        self.raw_file_service = RawFileService(directory)
        self.file_service = self.raw_file_service
        self.user_service = UserService()
        if Config().is_encrypted():
            self.file_service = EncryptedFileService(self.file_service)
        if Config().is_signed():
            self.file_service = SignedFileService(self.file_service)

    async def login(self, request, *args, **kwargs):
        data = b''
        while not request.content.at_eof():
            data += await request.content.read()
        data = json.loads(data.decode())
        try:
            uuid = self.user_service.add_session(data['username'], data['password'])
            response = web.Response(status=200, text=json.dumps({"Authorization": str(uuid)}))
        except Exception as e:
            response = web.Response(status=404, text=str(e))
        return response

    async def sign_up(self, request, *args, **kwargs):
        data = b''
        while not request.content.at_eof():
            data += await request.content.read()
        data = json.loads(data.decode())
        try:
            self.user_service.add_user(data['username'], data['password'])
            response = web.Response(status=200, text="Sign Up success")
        except Exception as e:
            response = web.Response(status=406, text=str(e))
        return response

    async def logout(self, request, *args, **kwargs):
        uuid = request.headers["Authorization"]
        try:
            self.user_service.logout(uuid)
            response = web.Response(status=200, text="Logout success")
        except Exception as e:
            response = web.Response(status=400, text=str(e))
        return response

    @authorize
    async def ls(self, request, *args, **kwargs):
        dir_listing = self.file_service.ls()
        return web.Response(text=json.dumps(dir_listing))

    @authorize
    async def cd(self, request, *args, **kwargs):
        directory = request.query['dir']
        cd = self.file_service.cd(directory)
        return web.Response(text=str(cd))

    @authorize
    async def pwd(self, request, *args, **kwargs):
        data = {"working_directory": self.file_service.workdir}
        return web.Response(text=json.dumps(data))

    @authorize
    async def read(self, request, *args, **kwargs):
        filename = request.query['filename']
        data = {"file_content": self.file_service.read(filename)}
        return web.Response(text=json.dumps(data))

    @authorize
    async def write(self, request, *args, **kwargs):
        result = ""
        stream = request.content
        while not stream.at_eof():
            line = await stream.read()
            result += line.decode("utf-8")
        filename = self.file_service.create(result)
        data = {"created_file": filename}
        return web.Response(text=json.dumps(data))

    @authorize
    async def read_metadata(self, request, *args, **kwargs):
        filename = request.query['filename']
        creation_date, modification_date, filesize = self.file_service.read_metadata(filename)
        data = {"creation_date": creation_date,
                "modification_date": modification_date,
                "file_size": filesize}
        return web.Response(text=json.dumps(data))


def create_web_app(directory):
    app = web.Application()
    handler = Handler(directory)
    app.add_routes([
        web.get('/ls', handler.ls),
        web.put('/cd', handler.cd),
        web.get('/pwd', handler.pwd),
        web.get('/read', handler.read),
        web.get('/read_meta', handler.read_metadata),
        web.post('/write', handler.write),
        web.post('/login', handler.login),
        web.post('/logout', handler.logout),
        web.post('/sign_up', handler.sign_up)
    ])
    return app
