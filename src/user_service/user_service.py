import psycopg2
import uuid
from src.config import Config
from datetime import datetime, timedelta
from psycopg2 import sql


class UserService:

    def __init__(self):
        db = Config().get_param("Database", "db", "postgres")
        user = Config().get_param("Database", "username", "postgress")
        password = Config().get_param("Database", "password", "postgress")
        host = Config().get_param("Database", "host", "127.0.0.1")
        self.connection = psycopg2.connect(dbname=db, user=user, password=password, host=host)
        self.expiration_time = 60 * 60 * 24

    def add_user(self, username, password):
        if not self.is_user_exists(username):
            request = sql.SQL(f'''INSERT INTO  public."Users" (username, password)
                             VALUES ('{username}', '{password}')''')
            self._execute(request)
        else:
            raise ValueError('User already exists!')

    def get_user_id(self, username):
        request = sql.SQL(f'''SELECT * FROM public."Users" WHERE "username"='{username}' ''')
        response = self._execute(request)
        if len(response) > 0:
            return response[0][0]
        else:
            raise ValueError("User doesn't exists!")

    def add_session(self, username, password):
        if self.check_user(username, password):
            user_id = self.get_user_id(username)
            generated_uuid = uuid.uuid4()
            while self.is_uuid_exists(generated_uuid):
                generated_uuid = uuid.uuid4()
            expiration_time = datetime.utcnow() + timedelta(days=1)
            request = sql.SQL(f'''INSERT INTO public."Sessions" (user_id, uuid, expiration_date)
                         VALUES ({user_id}, '{generated_uuid}', '{expiration_time}')''')
            self._execute(request)
            return generated_uuid
        else:
            raise ValueError("User doesn't exists!")

    def check_user(self, username, password):
        request = sql.SQL(f'''SELECT * FROM public."Users" 
        WHERE "username"='{username}' AND "password"='{password}' ''')
        return len(self._execute(request)) > 0

    def is_user_exists(self, username):
        request = sql.SQL(f'''SELECT * FROM public."Users" WHERE "username"='{username}' ''')
        return len(self._execute(request)) > 0

    def delete_user(self, username):
        request = sql.SQL(f'''DELETE FROM public."Users" WHERE "username"='{username}' ''')
        self._execute(request)

    def check_authorization(self, uuid):
        if len(uuid) != 36:
            raise ValueError("Auth token is invalid!")
        request = sql.SQL(f'''SELECT * from public."Sessions" WHERE "uuid"='{uuid}' ''')
        response = self._execute(request)
        if len(response) > 0:
            if datetime.strptime(response[0][2][:-3], '%Y-%m-%d %H:%M:%S') > datetime.utcnow():
                return True
            else:
                raise ValueError("Session is expired!")
        else:
            raise ValueError("Session doesn't exists!")

    def is_uuid_exists(self, uuid):
        request = sql.SQL(f'''SELECT * from public."Sessions" WHERE "uuid"='{uuid}' ''')
        return len(self._execute(request)) > 0

    def logout(self, uuid):
        if self.check_authorization(uuid):
            request = sql.SQL(f'''DELETE FROM public."Sessions" WHERE "uuid"='{uuid}' ''')
            self._execute(request)

    def _execute(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        try:
            return cursor.fetchall()
        except psycopg2.ProgrammingError:
            self.connection.commit()
