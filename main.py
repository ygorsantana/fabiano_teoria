from typing import List, Optional
import os
import sqlite3
import base64
import datetime
import re
import sys
import pandas as pd
import numpy as np
import requests


USERS_TABLE = 'tio_gordo_users.csv'


class Currency:
    def __init__(self, *args, **kwargs):
        self.url = "https://www.alphavantage.co/query"
        self.api_key = "MC6NE9KMDFIWKVY5"

    def get_current_value(self, currency):
        querystring = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "USD",
            "to_currency": currency,
            "apikey": self.api_key,
        }

        response = requests.get(
            self.url,
            params=querystring,
        )

        return response.json()


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

    def __init__(self, database, calculator, metric_converter, *args, **kwargs):
        self.database = database
        self.options = {
            '1': calculator,
            '2': metric_converter,
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
            '2. Conversor de medidas',
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

        print('\n' * 10)
        self.options[option].main()
        print('\n' * 10)

        # input('\nAperte enter para continuar\n')


class Calculator:
    regex = r'(\d+) *(.) *(\d+)'

    def __init__(self, *args, **kwargs):
        self.expressions = {
            '*': self._multiplication,
            '/': self._division,
            '-': self._subtraction,
            '+': self._addition,
        }

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
            expression = input('Operacao (aperte 0 e enter para sair): ')
            if expression == '0':
                return

            matched = re.match(self.regex, expression)
            try:
                first_number, operator, second_number = matched.groups()
            except AttributeError:
                print('Formato invalido, use:')
                print('10 + 8')
                print('10 - 8')
                continue

            if operator not in self.expressions.keys():
                print('Operador nao reconhecido !!!')
                continue

            print(expression, end=" => ")
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


class MetricConverter:
    def __init__(self, *args, **kwargs):
        self.currency = Currency()
        self.functions = {
            '1': self.celsius_to_farenheit,
            '2': self.fahrenheit_to_celsius,
            '3': self.libra_to_kg,
            '4': self.kg_to_libra,
            '5': self.km_to_miles,
            '6': self.miles_to_km ,
            '7': self.usd_to_brl,
        }

    def _get_usd_value(self):
        data = self.currency.get_current_value('BRL')
        return float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])

    def celsius_to_farenheit(self):
        celsius = float(input('Digite a temperatura em Celsius: '))
        fah = celsius * 1.8 + 32
        print(f"=> {fah:.2f} F")

    def fahrenheit_to_celsius(self):
        fah = float(input('Digite a temperatura em Fahrenheit: '))
        cel = (fah - 32) / 1.8
        print(f"=> {cel:.2f} C")

    def libra_to_kg(self):
        libras = float(input('Digite o peso em lbs: '))
        kg = libras / 2.2046
        print(f"=> {kg:.2f} kg")

    def kg_to_libra(self):
        kg = float(input('Digite o peso em kg: '))
        libras = kg * 2.2046
        print(f"=> {libras:.2f} lbs")

    def km_to_miles(self):
        km = float(input('Digite a distancia em km: '))
        miles = km / 1.609
        print(f"=> {miles:.2f} milhas")

    def miles_to_km(self):
        miles = float(input('Digite a distancia em milhas: '))
        km = miles * 1.609
        print(f"=> {km:.2f} km") 

    def usd_to_brl(self):
        usd = float(input('Digite a quantidade em dolares: '))
        brl = usd * self._get_usd_value()
        print(f"=> R$ {brl:.2f}")

    def main(self):
        print('Bem vindo ao Conversor de Medidas')
        while True:
            print('1 - Conversor de Celsius para Fahrenheit')
            print('2 - Conversor de Fahrenheit para Celsius')
            print('3 - Conversor de libras para kg')
            print('4 - Conversor de kg para libras')
            print('5 - Conversor de km para milhas')
            print('6 - Conversor de milhas para km')
            print('7 - Conversor de dolar para real')
            print('8 - Voltar ao menu principal')

            option = input('Escolha uma das opcões acima (1 a 8): ')
            if option == '8':
                return
            elif option not in self.functions.keys():
                print('Opcao nao encontrada !!!')
                continue

            self.functions[option]()
            input('Aperte enter para continuar\n')


if __name__ == "__main__":
    database = Database()

    os.system('clear')
    menu = Menu(
        database,
        calculator=Calculator(),
        metric_converter=MetricConverter(),
    )
    # TODO: Converter medidas
    # TODO: Listar bolsa pela api
    # TODO: Gerador de numeros aleatorios
    # TODO: Easter egg
    while True:
        menu.show()
