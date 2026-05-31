from data.simulation.engine import Engine

class Factory:

    @staticmethod
    def create():
        return Engine()