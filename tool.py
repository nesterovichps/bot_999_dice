from bet import Dice
import random


class Tool():

    @staticmethod
    def random_chunk():
            randomize_chunk = Dice.get_chunk_name(int(round(random.random())))

            return Dice.get_bet_chance(randomize_chunk)
