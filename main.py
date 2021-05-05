# coding=utf8

import requests
import json
from bet import Dice
from tool import Tool
import random

# TODO: А это нахуй удалить
API_URL = "https://www.999dice.com/api/web.aspx"


class Game:
    """
    Основной класс бота
    """
    plot_temp = []
    args = None

    # Счетчик текущей ставки
    bet_number = 1

    # Ожидание выйграша
    wait_win = False

    # Идет компенсация ставки
    compensation = False

    # Ставка во время компенсации проиграла
    bet_lose = False

    # Увиличивать ли множатель
    more_factor = False

    # Последний баланс
    last_balance = 0

    # Стартовый множитель
    factor_bonus = 1

    # Количество побед во время компенсации
    count_win = 0

    # Количество проиграшей во время компенсации
    count_lose = 0

    # Сколько нужно получить что-бы окончательно компенсировать
    need_get = 0

    def __init__(self, args):
        self.START_BET = args.bet
        self.START_FACTOR = args.factor
        self.API_KEY = args.key
        self.args = args

        auth_data = json.loads(self.auth(login=args.login, password=args.password))
        self.dice = Dice(auth_data, args)

    def auth(self, login, password):
        """
        Авторизация

        :param login:
        :param password:
        :return: json object
        """
        auth_response = requests.post(API_URL, data={"Key": self.API_KEY, "a": "Login", "Username": login,
                                                     "Password": password}).content

        return auth_response

    def clear_compensation(self):
        """
        Ставит в дефолтные значения, переменные для алгоритма компенсации

        :return: void
        """
        self.wait_win = False
        self.factor_bonus = 1
        self.count_lose = 0
        self.count_win = 0

    def is_stop_balance(self):
        """
        Проверяет, не перешл ли баланс значения args.stop.

        :return: bool
        """
        return (self.args.stop >= self.last_balance and self.args.stop != -1) and (self.last_balance != 0)

    def enable_plot(self):
        """
        Рисует на плоте линии и показывает

        :return: void
        """
        import matplotlib.pyplot as plt

        plt.plot(self.plot_temp)
        plt.show()

    def leave(self):
        """
        Проверяет, стоит ли ипараметр viewplot на > 0

        :return: void
        """
        if self.args.viewplot:
            print "Show plot"

            self.enable_plot()

    def start(self):
        """
        Именно отсюда следует запускать бесконечный цикл бота

        :return: void
        """
        while True:
            print "=" * 20
            print "#{0}".format(self.bet_number)

            # Проверяет, не перешел ли баланс за значение которое задано ключем -s.
            if self.is_stop_balance():
                self.leave()
                exit("Balance equal stop balance")

            try:
                self.play()
            except KeyboardInterrupt:
                self.leave()
                exit("Exiting")

    def play(self):
        balance_response = 0

        # Получает рандомный чанк, куда будет ставится эта ставка.
        current_low, current_high = Tool.random_chunk()

        bet_count = self.START_BET
        comp_factor = self.START_FACTOR

        # Нужна ли компенсация баланса.
        if self.compensation:
            print "compensation = %i" % self.compensation

            print "*{0} Bet, Factor {1}".format(comp_factor, self.factor_bonus)

            bet_count = (bet_count * comp_factor)

            if self.count_lose > 0:
                self.bet_lose = True
                self.more_factor = True
                self.count_lose = 0

            if self.bet_lose:
                # Если все ставки проигрывают, увиличваем каждый раз счетчик.
                if self.more_factor:
                    self.factor_bonus *= self.args.comprate

                    if (self.factor_bonus >= self.args.maxcomp) and (self.args.maxcomp != 0):
                        print "MAX Factor bonus. Compensation is now disable"
                        self.compensation = False

                    self.more_factor = False

                # Изначально factor_bonus равен нулю
                if self.factor_bonus > 0:
                    bet_count *= self.factor_bonus

                # Если баланс достиг нужного значения.
                if self.last_balance >= self.need_get:
                    print "Last balance more or equal value 'need get balance'"

                    bet_count = self.START_BET
                    self.compensation = False
            else:
                # С каждым проиграшем, значение count_win ставится на 0.
                if self.count_win >= (self.args.count-1):
                    bet_count = self.START_BET
                    self.compensation = False

        print "Current bet: {0}".format(bet_count)

        bet_response = self.dice.bet(pay=bet_count, low=current_low, high=current_high)
        bet_dict = json.loads(bet_response)

        try:
            balance_response = bet_dict["StartingBalance"]
        except KeyError:
            self.leave()
            exit("Error: Balance is small")

        # Если хотя бы раз проиграла, то ждем победы хотябы одной ставки.
        if self.wait_win:
            # В отличии от нижнего участка кода, здесь баланс получается сразу
            # Постоянно это делать нельзя, по причине того что у dice стоят жесткие
            # таймауты на получения текущего баланса.
            balance = self.dice.get_balance()

            # Баланс, который нужно будетт получить, если начнет проиграет хотя бы 1 раз, после этой ставки
            self.need_get = (balance + self.args.bet)

            print "You balance for wait win: {0}, need get value {1}".format(balance, self.need_get)

            # Если ставка выйграла
            if int(balance) >= int(self.last_balance):
                print "Game: ++"

                self.compensation = True
                self.clear_compensation()
            else:
                print "Game: --"
        else:
            if self.compensation or (random.randint(0, 3) == 2):
                balance_response = self.dice.get_balance()
                print "Debug balance: %i" % balance_response

            # Баланс ставки можно узнать в этом случаее только после её совершения.
            if balance_response >= self.last_balance:
                print "Game: +"

                if self.compensation:
                    self.count_lose = 0
                    self.count_win += 1
                    self.more_factor = False
            else:
                print "Game: -"

                # Если уже идет компенсация баланса, то нету смысла обнулять значения
                if not self.compensation:
                    self.wait_win = True

                if self.compensation:
                    if self.bet_lose:
                        self.count_win = 0

                    self.count_lose += 1

        self.last_balance = balance_response

        print "Current balance: last %i" % self.last_balance

        self.bet_number += 1

        if self.args.viewplot == 1:
            self.plot_temp.append(balance_response)
