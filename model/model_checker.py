__author__ = "Olga Ivanova"
__date__ = "28.07.2016"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"

#TODO singleton
import numpy as np
from .model import Model


class ModelChecker:

    def __init__(self):
        pass

    @staticmethod
    def check_all_constraints(model):
        if not isinstance(model, Model):
            model = Model(model)

        if ModelChecker.check_self_edges(model) and \
           ModelChecker.check_edges_constraint(model) and \
           ModelChecker.check_regulators_constraints(model):
            return True
        return False

    @staticmethod
    def check_self_edges(model):
        if 1 in np.diagonal(model.get_matrix()):
            return False
        return True

    @staticmethod
    #TODO check only for topology (not for model with params): rewrite or rename
    # Check is there are only 2 incoming edges for each node
    def check_edges_constraint(model):
        r = np.sum(model.get_matrix(), axis=1)
        for i in np.nditer(r):
            if i > 2:
                return False
        return True

    # Check is both regulator connected
    @staticmethod
    def check_regulators_constraints(model):
        r = np.sum(model.get_matrix()[2:4, 0:2], axis=0)
        for i in np.nditer(r):
            if i == 0:
                return False
        return True


    @staticmethod
    def has_competing_connections(model):
        matrix = model.get_matrix()
        columns = np.squeeze(np.array((matrix != 0).sum(0)))
        return sum(columns > 1)


    #TODO model should return the "name" of connection
    #TODO Now it's working as a crutch
    @staticmethod
    def regulators_connected(model):
        connections = model.get_connections()
        correction = {}
        if ("R1", "R2") in connections.keys():
            correction[("R1", "R2")] = connections[("R1", "R2")]
        if ("R2", "R1") in connections.keys():
            correction[("R2", "R1")] = connections[("R2", "R1")]
        return correction

    @staticmethod
    def same_model(model1, model2):
        return np.equal(model1.get_matrix(), model2.get_matrix()).all()