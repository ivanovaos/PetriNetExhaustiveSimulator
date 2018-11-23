__author__ = "Olga Ivanova"
__date__ = "17.02.2017"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"

from model.model_handler import ModelHandler


class PetrinetReader:

    path = ""

    def __init__(self):
        pass

    @staticmethod
    def set_path(path):
        PetrinetReader.path = path

    @staticmethod
    def read_petrinet(filename):
        with open(PetrinetReader.path + filename, "r") as f:
                lines = f.read().splitlines()
        pnS = {}
        for line in lines:
            petrinet_data = line.split("_")
            model = ModelHandler.read_one_model_line(petrinet_data[0])
            idx = int(petrinet_data[1])
            pnS[model] = idx

        return pnS

