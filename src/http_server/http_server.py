from aiohttp import web
from src.config import Config
from src.file_service import RawFileService, SignedFileService, EncryptedFileService
import json


class Handler:

    def __init__(self):
        self.raw_file_service = RawFileService(".")
        self.file_service = self.raw_file_service
        if Config().is_encrypted():
            self.file_service = EncryptedFileService(self.file_service)
        if Config().is_signed():
            self.file_service = SignedFileService(self.file_service)

    async def ls(self, request, *args, **kwargs):
        dir_listing = self.file_service.ls()
        return web.Response(text=json.dumps(dir_listing))

    async def cd(self, request, *args, **kwargs):
        directory = request.query['dir']
        cd = self.file_service.cd(directory)
        return web.Response(text=str(cd))

    async def pwd(self, request, *args, **kwargs):
        data = {"working_directory": self.file_service.workdir}
        return web.Response(text=json.dumps(data))

    async def read(self, request, *args, **kwargs):
        filename = request.query['filename']
        data = {"file_content": self.file_service.read(filename)}
        return web.Response(text=json.dumps(data))

    async def write(self, request, *args, **kwargs):
        result = ""
        stream = request.content
        while not stream.at_eof():
            line = await stream.read()
            result += line.decode("utf-8")
        filename = self.file_service.create(result)
        data = {"created_file": filename}
        return web.Response(text=json.dumps(data))

    async def read_metadata(self, request, *args, **kwargs):
        filename = request.query['filename']
        creation_date, modification_date, filesize = self.file_service.read_metadata(filename)
        data = {"creation_date": creation_date,
                "modification_date": modification_date,
                "file_size": filesize}
        return web.Response(text=json.dumps(data))


def create_web_app():
    app = web.Application()
    handler = Handler()
    app.add_routes([
        web.get('/ls', handler.ls),
        web.put('/cd', handler.cd),
        web.get('/pwd', handler.pwd),
        web.get('/read', handler.read),
        web.get('/read_meta', handler.read_metadata),
        web.post('/write', handler.write)
    ])
    return app