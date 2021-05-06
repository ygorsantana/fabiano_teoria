import requests
import sys
import os
import time


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


class TerminalClear:
    @staticmethod
    def clear_window():
        if sys.platform == 'linux':
            os.system('clear')
        else:
            os.system('cls')

    @staticmethod
    def main():
        TerminalClear.clear_window()


class CustomPrint:
    def credits(self, *string):
        unique_text = '\n'.join(string)
        for char in unique_text:
            print(char, end='', flush=True)
            time.sleep(0.02)
        print()
    
    def delayed(self, string, time_to_sleep):
        for char in string:
            print(char, end='', flush=True)
            time.sleep(time_to_sleep)
        print()
