# coding=utf8

import argparse
from main import Game

parse = argparse.ArgumentParser()

parse.add_argument("--login", "-l", type=str, help="Логин", required=True)
parse.add_argument("--password", "-p", type=str, help="Пароль", required=True)
parse.add_argument("--key", "-k", type=str, help="API ключ", required=True)

parse.add_argument("--bet", "-b", type=int, help="По сколько ставить", default=40)
parse.add_argument("--factor", "-f", type=int, help="Множитель", default=4)
parse.add_argument("--count", "-c", type=int, help="Количество ставок", default=2)
parse.add_argument("--stop", "-s", type=int, help="На каком числе остановится", default=-1)

parse.add_argument("--comprate", "-r", type=int, help="На сколько увеличивать при компенсации", default=6)
parse.add_argument("--maxcomp", "-m", type=int, help="Максимальное значение множителя компенсации. "
                                                     "При достежнии этого значения, выходит из цикла.", default=0)

parse.add_argument("--viewplot", "-v", type=int, help="Показать в конце график", default=-1)
parse.add_argument("--timeout", "-t", type=int, help="Таймаут", default=30)

args = parse.parse_args()

Game = Game(args)
Game.start()
