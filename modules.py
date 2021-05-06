from utils import Currency

import random
import re
import requests


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


class PrizeDraw:
    def main(self):
        while True:
            try:
                print('Use o atalho Ctrl + C para sair do sorteio')
                n1 = int(input('Digite o primeiro valor: '))
                n2 = int(input('Digite o último valor: '))
                print(f'\nO valor sorteado foi: {random.randint(n1, n2)}\n')
            except KeyboardInterrupt:
                break


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
        try:
            return float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        except:
            return 5.35

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



class Exchange:
    def __init__(self, *args, **kwargs):
        self.url = "https://www.alphavantage.co/query"
        self.api_key = "MC6NE9KMDFIWKVY5"
        self._btc = None
        self._usd = None
        self._eth = None
        self._doge = None
        self._gbp = None
        self._jpy = None

        self.currencies = {
            'BTC': self.btc,
            'USD': self.usd,
            'ETH': self.eth,
            'DOGE': self.doge,
            'GBP': self.gbp,
            'JPY': self.jpy,
        }

    @property
    def btc(self):
        if self._btc:
            return self._btc

        querystring = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "BTC",
            "to_currency": "BRL",
            "apikey": self.api_key,
        }

        response = requests.get(
            self.url,
            params=querystring,
        )
        try:
            self._btc = float(response.json()['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        except KeyError:
            self._btc = 306564.67981200

        return self._btc

    @property
    def usd(self):
        if self._usd:
            return self._usd

        querystring = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "USD",
            "to_currency": "BRL",
            "apikey": self.api_key,
        }

        response = requests.get(
            self.url,
            params=querystring,
        )
        try:
            self._usd = float(response.json()['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        except KeyError:
            self._usd = 5.35

        return self._usd

    @property
    def eth(self):
        if self._eth:
            return self._eth

        querystring = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "ETH",
            "to_currency": "BRL",
            "apikey": self.api_key,
        }

        response = requests.get(
            self.url,
            params=querystring,
        )
        try:
            self._eth = float(response.json()['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        except KeyError:
            self._eth = 18055.23

        return self._eth

    @property
    def doge(self):
        if self._doge:
            return self._doge

        querystring = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "DOGE",
            "to_currency": "BRL",
            "apikey": self.api_key,
        }

        response = requests.get(
            self.url,
            params=querystring,
        )
        try:
            self._doge = float(response.json()['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        except KeyError:
            self._doge = 3.41

        return self._doge

    @property
    def gbp(self):
        if self._gbp:
            return self._gbp

        querystring = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "GBP",
            "to_currency": "BRL",
            "apikey": self.api_key,
        }

        response = requests.get(
            self.url,
            params=querystring,
        )
        try:
            self._gbp = float(response.json()['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        except KeyError:
            self._gbp = 7.46

        return self._gbp

    @property
    def jpy(self):
        if self._jpy:
            return self._jpy

        querystring = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "JPY",
            "to_currency": "BRL",
            "apikey": self.api_key,
        }

        response = requests.get(
            self.url,
            params=querystring,
        )
        try:
            self._jpy = float(response.json()['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        except KeyError:
            self._jpy = 0.049

        return self._jpy

    def get_col_size_value(self):
        return max([len(f'{x:.3f}') for x in self.currencies.values()])

    def main(self):
        print(
            *[f'{x:^{self.get_col_size_value()}}' for x in self.currencies.keys()],
            sep=' | ',
        )
        print(
            *[f'{x:{self.get_col_size_value()}.3f}' for x in self.currencies.values()],
            sep=' | ',
        )
        print('\n' * 5)

        input('Aperte enter para continuar... ')
