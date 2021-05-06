from database import Database
from menu import Menu
from modules import Calculator
from modules import Exchange
from modules import MetricConverter
from modules import PrizeDraw

import os


if __name__ == "__main__":
    database = Database()

    os.system('clear')
    menu = Menu(
        database,
        calculator=Calculator(),
        metric_converter=MetricConverter(),
        prize_draw=PrizeDraw(),
        exchange=Exchange(),
    )

    while True:
        menu.show()
