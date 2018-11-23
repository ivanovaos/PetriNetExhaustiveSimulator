#!/usr/bin/env python

__author__ = "Olga Ivanova"
__date__ = "20.07.2016"
__version__ = "2.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"

# Python 3.3.2

import numpy as np
import random

#TODO Load it through the config
#TODO make it array?
places_names_default = {0: "R1", 1: "R2", 2: "G1", 3: "G2"}
places_names = {"R1": 0, "R2": 1, "G1": 2, "G2": 3}


class Model:

    def __init__(self, matrix, places=places_names_default):
        #TODO static field?
        self.places_names = places
        self.matrix = np.matrix(matrix)

    @staticmethod
    def deepcopy_model(model):
        matrix = np.copy(model.get_matrix())
        return Model(matrix)

    def equal(self, model):
        return (np.equal(self.get_matrix(), model.get_matrix())).all()

    def get_matrix(self):
        return self.matrix

    def set_places_names(self, places_names):
        self.places_names = places_names

    def get_places_names(self):
        return self.places_names

    def get_row_by_name(self, name):
        nrow = -1
        #TODO make this number equals num of col/row names
        for n, place_name in self.places_names.items():
            if place_name == name:
                nrow = n
        return self.matrix[nrow, :]

    def get_column_by_name(self, name):
        ncol = -1
        for n, place_name in self.places_names.items():
            if place_name == name:
                ncol = n
        return self.matrix[:, [ncol]]

    def get_connections(self):
        connection_names = {}
        nonzeros = self.get_all_nonzero_elements()

        for idx in nonzeros:
            connection = (self.places_names[idx[1]], self.places_names[idx[0]])
            connection_names[connection] = nonzeros[idx]

        return connection_names

    def get_connections_combined(self):
        connections = self.get_connections()
        reordered = {}

        for conn, val in connections.items():
            if conn[1] not in reordered.keys():
                reordered[conn[1]] = {}
            reordered[conn[1]].update({conn[0]: val})

        return reordered

    #Reset incoming connection, for mutant with off genes
    def reset_incoming_connection(self, placename):
        connections = self.get_connections()

        for c in connections.keys():
            if placename in c[1]:
                #TODO refactor
                self.set_value_by_index(places_names[c[1]], places_names[c[0]], 0)

        return self.matrix

    def get_connection_num(self):
        return np.count_nonzero(self.matrix)

    def get_connection_indexes(self):
        nonzero_elements = np.array(self.matrix.nonzero())
        return nonzero_elements.transpose()

    def get_value_by_index(self, x, y):
        return self.matrix[x, y]

    def set_value_by_index(self, x, y, value):
        self.matrix[x, y] = value

    def get_all_nonzero_elements(self):
        nonzero = self.get_connection_indexes()

        nonzero_val = {}
        for z in nonzero:
            x = np.squeeze(np.asarray(z))
            nonzero_val[x[0], x[1]] = (self.matrix[x[0], x[1]])

        return nonzero_val

    def get_multistring_model_repr(self):
        model_str = " " + str(self.matrix).replace('[', '').replace(']', '')
        return model_str

    def __str__(self):
        model_str = self.get_multistring_model_repr()
        return model_str.replace(" ", '').replace("\n", '')