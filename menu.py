from database import User
from utils import Bcolors
from utils import CustomPrint
from utils import IntegrityError
from utils import TerminalClear

import re


class Menu:
    regex_hard_password_validator = r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[*.!@$%^&(){}[]:;<>,.?/~_+-=|\]).{8,32}$'
    regex_password_validator = r'^(?=.*[a-zA-Z0-9]).{3,}$'

    def __init__(self, database, calculator, metric_converter, prize_draw, exchange, *args, **kwargs):
        self.database = database
        self.print = CustomPrint()
        self.options = {
            '1': calculator,
            '2': metric_converter,
            '3': prize_draw,
            '4': exchange,
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
            TerminalClear.clear_window()
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

    def credits(self):
        self.print.credits(
            'Bruna Timoteo 73389',
            'Davi Henrique 102227',
            'Gabriel Pinheiro 103362',
            'Felipe Godoy 104496',
            'Julie Ribeiro da Silva 104650',
            'Rafael Mercatelli 103398',
            'Ygor Santana 102928',
            '',
            'Foi um prazer ter feito esse trabalho e',
            'repassado o conhecimento aos meus colegas',
        )

    def show(self):
        self.header()
        print(
            f'1. Calculadora',
            '2. Conversor de medidas',
            '3. Sortear numero aleatorio',
            '4. Bolsa de valores',
            '5. Limpar a tela',
            '6. Créditos',
            '7. Sair',
            sep='\n',
        )

        option = input('\nDigite uma opcao (de 1 a 7): ')
        if option == '7':
            self.print.delayed('\nSentiremos sua falta !!!\n', 0.07)
            exit(0)
        elif option == '6':
            print('\n')
            self.credits()
            print('\n')
            input('Aperte Enter para continuar... ')
            return
        elif option not in self.options.keys():
            print('Opcao invalida !!!')
            return

        print('\n' * 20)
        self.options[option].main()
        print('\n' * 20)
