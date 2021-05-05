# coding=utf8

import json
import requests

import time

class Dice():
    API_URL = "https://www.999dice.com/api/web.aspx"
    args = None

    def __init__(self, auth, args):
        self.session_cookie = auth["SessionCookie"]
        self.client_seed = auth["ClientSeed"]

        self.args = args

    def parse_result(self, result):
        """
        Парсит содержимое ресультата (json)

        :param result:
        :return:    dict    Результат парсинга json
        """

        return json.loads(result)

    def bet(self, pay=1, low=0, high=949999):
        """
        Делает ставку

        Для 95% значения low/high: 0 - 949999    50000 - 999999

        :param pay: int     Количество
        :param low: int     Начало чанков
        :param high: int     Конец чанков
        :return: json   Результат
        """

        result = None

        try:
            result = requests.post(self.API_URL,
                                   data={"a": "PlaceBet", "s": self.session_cookie, "PayIn": pay, "Low": low,
                                         "High": high, "ClientSeed": self.client_seed, "Currency":
                                             "btc", "ProtocolVersion": 2}, timeout=self.args.timeout)
        except Exception, e:
            print "Error: %s" % e.message

            time.sleep(4)

            self.bet(pay=pay, low=low, high=high)
        else:
            return result.content

    @staticmethod
    def get_bet_chance(mode="low"):
        """
        Возвращает чанки для low/high ставок

        :param mode:
        :return:
        """

        low_number = high_number = None

        if mode == "low":
            low_number = 0
            high_number = 949999

        elif mode == "high":
            low_number = 50000
            high_number = 999999

        return low_number, high_number

    def get_balance(self):
        """
        Возвращает баланс.
        В случаее, если баланс вернуть не может, то, ожидает 4 секунды и повторяет попытку.

        :return: int    Баланс
        """

        try:
            result = requests.post(self.API_URL, data={"a": "GetBalance", "s": self.session_cookie},
                                   timeout=self.args.timeout)
        except Exception, e:
            print "Error: %s" % e.message

            time.sleep(4)
            return self.get_balance()

        extract_balance = -1

        try:
            extract_balance = self.parse_result(result.content)["Balance"]
        except KeyError:
            pass

        if extract_balance == -1:
            time.sleep(4)

            return self.get_balance()

        return extract_balance

    @staticmethod
    # @TODO: не используется
    def is_win(last, current):
        """
        Проверяет, выйграла ли ставка.

        :param last:
        :param current:
        :return:
        """

        if last > current:
            return False

        return True

    @staticmethod
    def get_chunk_name(random_id):
        chuck_list = ["low", "high"]

        return chuck_list[random_id]

