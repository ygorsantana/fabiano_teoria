from typing import List, Optional
import os
import sqlite3
import base64
import datetime
import re
import sys


def query_commit(funcao):
    def wrapper(self, *args):
        result = funcao(self, *args)
        self.con.commit()
        return result
    return wrapper


class Database:
    def __init__(self, *args, **kwargs):
        self._cursor = None
        self.con = sqlite3.connect('tio_gordo.db')
        self.create_tables()

    def create_tables(self, *args, **kwargs):
        query = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                login TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TEXT,
                is_active INTEGER DEFAULT 1
            );
        '''
        self.cursor.execute(query)

    @query_commit
    def insert(self, query):
        self.cursor.execute(query)

    @property
    def cursor(self):
        if self._cursor:
            return self._cursor

        self._cursor = self.con.cursor()
        return self._cursor


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
        self.id = fields[0]
        self.first_name = fields[3]
        self.last_name = fields[4]
        self.created_at = fields[5]
        self.is_active = fields[6]

    def create(self):
        query = '''
            INSERT INTO users (login, password, first_name, last_name, created_at)
            VALUES ('{login}', '{password}', '{first_name}', '{last_name}', '{created_at}')
        '''.format(
            login=self.login,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
            created_at=datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        )
        self.database.insert(query)

    def authenticate(self):
        query = f'''
            SELECT
                id, login, password, first_name, last_name, created_at, is_active
            FROM
                users
            WHERE
                login = '{self.login}'
                AND password = '{self.password}'
                AND is_active = 1
        '''
        self.database.cursor.execute(query)
        if user := self.database.cursor.fetchall():
            self._authenticated = True
            self._fill_fields(user[0])
            return user[0]
        return False

    @property
    def is_authenticated(self):
        return self._authenticated

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'

        return f'{self.login}'


class TerminalClear:
    @staticmethod
    def main():
        if sys.platform == 'linux':
            os.system('clear')
        else:
            os.system('cls')


class Menu:
    def __init__(self, database, calculator, *args, **kwargs):
        self.database = database
        self.options = {
            '1': calculator,
            '5': TerminalClear,
        }

        self.initial_options = {
            '1': self._login,
            '2': self._sign_in,
        }

        print(
            '1. Login',
            '2. Cadastre-se',
            sep='\n',
        )
        option = input('Selecione uma opção acima: ')
        logged = self.initial_options[option]()
        if not logged:
            return

    def _login(self):
        login = input('Login: ')
        password = input('Password: ')

        self.user = User(login, password, database=self.database)
        self.user.authenticate()
        if not self.user.is_authenticated:
            print("Usuario nao encontrado")
            return False
        
        return True

    def _sign_in(self):
        login = input('Login: ')
        password = input('Password: ')
        first_name = input('First Name (can be empty): ')
        last_name = input('Last Name (can be empty): ')

        self.user = User(
            login,
            password,
            database=self.database,
            first_name=first_name,
            last_name=last_name,
        )
        try:
            self.user.create()
        except sqlite3.IntegrityError:
            print('Usuario ja cadastrado')
            return False

        self.user.authenticate()
        return True

    def header(self):
        if self.user.is_authenticated:
            print(f'Usuario: {self.user}\n')

    def show(self):
        self.header()
        print(
            f'1. Calculadora',
            '2. Gerar a lista usando o comando FOR',
            '3. Gerar a lista usando a função MAP',
            '4. Gerar a lista usando a função FILTER',
            '5. Limpar a tela',
            '6. Sair',
            sep='\n',
        )

        option = input('\nDigite uma opcao (de 1 a 6): ')
        if option not in self.options.keys():
            print('Opcao invalida !!!')
            return

        self.options[option].main()
        input('Aperte enter para continuar')


class Calculator:
    regex = r'(\d+) *([-+*/]) *(\d+)'

    def main(self):
        print('Bem vindo a Calculadora')
        print('Por favor digite a expressao desejada')
        print('Exemplo:')
        print('10 * 8')
        print('10 / 8')
        print('10 + 8')
        print('10 - 8')
        # print('Invalidos:')
        # print('10 x 8')
        # print('10 soma 8')
        expression = input()
        self.calc(expression)

    def calc(self, string):
        self.expressions = {
            '*': self._multiplication,
            '/': self._division,
            '-': self._subtraction,
            '+': self._addition,
        }
        matched = re.match(self.regex, string)
        first_number, operator, second_number = matched.groups()
        if operator not in self.expressions.keys():
            print('Operador nao reconhecido !!!')
            return

        print(self.expressions[operator](float(first_number), float(second_number)))

    def _multiplication(self, a, b):
        return a * b

    def _division(self, a, b):
        if b == 0:
            return "Nao eh possivel divisao por zero"
        return a / b

    def _subtraction(self, a, b):
        return a - b

    def _addition(self, a, b):
        return a + b


if __name__ == "__main__":
    database = Database()

    os.system('clear')
    menu = Menu(
        database,
        calculator=Calculator(),
    )
    # TODO: Converter medidas
    # TODO: Listar bolsa pela api
    # TODO: Gerador de numeros aleatorios
    # TODO: Easter egg
    while True:
        menu.show()
