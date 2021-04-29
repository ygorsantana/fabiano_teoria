from typing import List, Optional
import os
import sqlite3
import base64
import datetime
import re
import sys
import pandas as pd
import numpy as np


USERS_TABLE = 'tio_gordo_users.csv'


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class IntegrityError(Exception):
    pass


def df_commit(funcao):
    def wrapper(self, *args):
        result = funcao(self, *args)
        self.df.to_csv(USERS_TABLE, index=False)
        return result
    return wrapper


class Database:
    def __init__(self, *args, **kwargs):
        self.create_file()
        self.df = pd.read_csv(USERS_TABLE)
        self.df = self.df.replace(np.nan, '', regex=True)

    def create_file(self):
        if os.path.exists(USERS_TABLE):
            return

        columns=[
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


class TerminalClear:
    @staticmethod
    def main():
        if sys.platform == 'linux':
            os.system('clear')
        else:
            os.system('cls')


class Menu:
    regex_hard_password_validator = r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[*.!@$%^&(){}[]:;<>,.?/~_+-=|\]).{8,32}$'
    regex_password_validator = r'^(?=.*[a-zA-Z0-9]).{3,}$'

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

        while True:
            print(
                '1. Login',
                '2. Cadastre-se',
                sep='\n',
            )
            option = input('Selecione uma opção acima: ')
            logged, msg = self.initial_options[option]()
            self.options['5'].main()
            if logged:
                break
            print(msg)

    def _login(self):
        login = input('Login: ')
        password = input('Password: ')

        self.user = User(login, password, database=self.database)
        self.user.authenticate()
        if not self.user.is_authenticated:
            return False, "Usuario e/ou senha invalidos"

        return True, ""

    def _sign_in(self):
        login = input('Login: ')

        password = None
        while not password:
            _password = input('Password: ')
            if re.match(self.regex_password_validator, _password):
                password = _password
            else:
                print('Por favor insira uma senha mais segura')

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
        except IntegrityError:
            return False, f"{Bcolors.FAIL}Usuario {login} ja cadastrado{Bcolors.ENDC}"

        self.user.authenticate()
        return True, ""

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
        input('\nAperte enter para continuar\n')


class Calculator:
    regex = r'(\d+) *([-+*/]) *(\d+)'

    def main(self):
        print('Bem vindo a Calculadora')
        print('Por favor digite a expressao desejada')
        print('Para sair da calculadora, digite 0 e aperte enter')
        print('Exemplo:')
        print('10 * 8')
        print('10 / 8')
        print('10 + 8')
        print('10 - 8')

        while True:
            expression = input('Operacao: ')
            if expression == '0':
                return
            print(expression, end=" => ")
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
        try:
            return a / b
        except ZeroDivisionError as e:
            return "Nao eh possivel efetuar uma divisão por zero"

    def _subtraction(self, a, b):
        return a - b

    def _addition(self, a, b):
        return a + b


class ConversorDeMedidas:
    def __init__(self, *args, **kwargs):
        self.functions = {
            '1': self.celsius_to_farenheit(),
            '2': self.fahrenheit_to_celsius(),
            '3': self.libra_to_kg(),
            '4': self.kg_to_libra(),
            '5': self.km_to_miles(),
            '6': self.miles_to_km() ,
            '7': self.funcRealDol(),
            '8': self.close(),
        }

    def celsius_to_farenheit(self):
        celsius = float(input('Digite a temperatura em Celsius: '))
        fah = celsius * 1.8 + 32
        print(f"\n {fah:.2f}ºF")

    def fahrenheit_to_celsius(self):
        fah = float(input('Digite a temperatura em Fahrenheit: '))
        cel = (fah - 32) / 1.8
        print(f"\n {cel:.2f}ºC")

    def libra_to_kg(self):
        libras = float(input('Digite o peso em lbs: '))
        kg = libras / 2.2046
        print(f"\n {kg:.2f} kg")

    def kg_to_libra(self):
        kg = float(input('Digite o peso em kg: '))
        libras = kg * 2.2046
        print(f"\n {libras:.2f} lbs")

    def km_to_miles(self):
        km = float(input('Digite a distancia em km: '))
        miles = km / 1.609
        print(f"\n {miles:.2f} milhas")

    def miles_to_km(self):
        miles = float(input('Digite a distancia em milhas: '))
        km = miles * 1.609
        print(f"\n {km:.2f} km") 

    def funcRealDol(self):
        usd = float(input('Digite quantos dólares você tem a sorte de ter agora: '))
        brl = usd * 23.73
        print(f"\n Com US$ {usd} vc tem aproximadamente R$ {brl:.2f}!")

    def main(self):
        while True:
            print('\n' + 50*'*')
            print('Bem vindo ao Conversor de Medidas')
            print('1 - Conversor de Celsius para Fahrenheit')
            print('2 - Conversor de Fahrenheit para Celsius')
            print('3 - Conversor de libras para kg')
            print('4 - Conversor de kg para libras')
            print('5 - Conversor de km para milhas')
            print('6 - Conversor de milhas para km')
            print('7 - Conversor aproximado de dólares para reais do futuro no ano de 2032')
            print('8 - Encerrar programa')

            option = int(input('Escolha uma das opcões acima (1 a 8):'))
            if option not in self.functions.keys():
                print('Opcao nao encontrada !!!')
                continue

            self.expressions[option]()
            input('Digite uma tecla para voltar ao menu inicial')


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
