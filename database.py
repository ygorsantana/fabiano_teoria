from utils import df_commit
from utils import IntegrityError
from utils import USERS_TABLE

import base64
import datetime
import os

import numpy as np
import pandas as pd


class Database:
    def __init__(self, *args, **kwargs):
        self.create_file()
        self.df = pd.read_csv(USERS_TABLE)
        self.df = self.df.replace(np.nan, '', regex=True)

    def create_file(self):
        if os.path.exists(USERS_TABLE):
            return

        columns = [
            'id',
            'first_name',
            'last_name',
            'login',
            'password',
            'created_at',
            'is_active',
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(USERS_TABLE, index=False)

    def get_next_index(self):
        return len(self.df) + 1

    @df_commit
    def insert(self, data):
        data['id'] = self.get_next_index()
        if not self.df.query(f"login == '{data['login']}'").empty:
            raise IntegrityError()

        self.df = self.df.append(data, ignore_index=True)
        return True

    def query(self, query):
        return self.df.query(query)


class User:
    id: int = 0
    login: str = None
    password: str = None
    first_name: str = ''
    last_name: str = ''
    created_at: str = None
    is_active: int = 0

    # TODO: update first name and password

    def __init__(self, login, password, database, *args, **kwargs):
        self.login = login
        self._password = password
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self._authenticated = False
        self.database = database

    @property
    def password(self):
        return base64.b64encode(self._password.encode('ascii')).decode('ascii')

    def _fill_fields(self, fields):
        self.id = fields['id']
        self.first_name = fields['first_name']
        self.last_name = fields['last_name']
        self.created_at = fields['created_at']
        self.is_active = fields['is_active']

    def create(self):
        data = {
            'login': self.login,
            'password': self.password,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            'is_active': 1,
        }
        self.database.insert(data)

    def authenticate(self):
        filters = [
            f"login == '{self.login}'",
            f"password == '{self.password}'",
            "is_active == 1",
        ]
        df = self.database.query(' and '.join(filters))
        if not df.empty:
            user = df.to_dict(orient='records')[0]
            self._authenticated = True
            self._fill_fields(user)
            return user
        return False

    @property
    def is_authenticated(self):
        return self._authenticated

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'

        return f'{self.login}'
