from __future__ import division

__author__ = "Olga Ivanova"
__date__ = "20.07.2016"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"

# Python 3.3.2

import itertools
import numpy as np
import logging
import math

from .model import Model
from .model_handler import ModelHandler
from .model_checker import ModelChecker

#TODO should be in config?
interactions = {"weak_activation": 1, "strong_activation": 5, "weak_inhibition": -1,
                "strong_inhibition": -5}

def generate_filtered_topologies(path="topologies/", is_write=False):

    all_topologies = generate_possible_topologies()
    filtered_topologies = [Model(t) for t in all_topologies if ModelChecker.check_all_constraints(t)]

    logging.info("Generating topologies for models...")

    if is_write:
        ModelHandler.set_path(path)
        ModelHandler.write_models(filtered_topologies, is_model=False)

    logging.info(str(len(filtered_topologies)) + " topologies have been generated")
    return filtered_topologies


def generate_possible_topologies():
    iter_combinations = itertools.product([0, 1], repeat=4)
    combinations = [i for i in iter_combinations]
    all_models = itertools.product(combinations, repeat=4)

    return all_models


def generate_models_with_parameters(topologies, path="models/", is_write=False):

    models_with_params = {}
    n_expected = 0

    for idx, topology in enumerate(topologies):
        topology_str = str(topology)

        logging.info("Generating permutations of all parameters for topology #" + str(idx))
        logging.debug("\n" + topology.get_multistring_model_repr())

        #TODO substitute magic number
        n_expected_current = calculate_n_of_models(topology.get_connection_num(), 4)
        logging.debug("Expected number of models for topology #" + str(idx) + ": " + str(n_expected_current))

        n_expected += n_expected_current
        new_models = generate_models_for_topology(topology)
        models_with_params[topology_str] = new_models

        if is_write:
            ModelHandler.path = path
            #TODO temp comment!
            ModelHandler.write_models_to_file(new_models)#, topology_str=topology_str)

        logging.info("Generating finished, n models " + str(len(new_models)) + " topology #" + str(idx))

    logging.info("Generating has been finished for all of the models")
    logging.info("Expected number of models: " + str(n_expected))

    return models_with_params


def calculate_n_of_models(n_connections, n_params):
    return math.pow(n_params, n_connections)


# Changing 1ths in models to all possible combinations with parameters
def generate_models_for_topology(topology, params=interactions.values()):
    models_with_params = []

    #TODO handle old numpy exception
    n_params = topology.get_connection_num()
    permutations_params = permute_params_for_nonzero(params, n_params)
    nonzero_elements = topology.get_connection_indexes()

    for perm in permutations_params:
        tmp_model = Model(topology.get_matrix())
        for x, value in zip(nonzero_elements, perm):
            x = np.squeeze(np.asarray(x))
            tmp_model.set_value_by_index(x[0], x[1], value)

        models_with_params.append(tmp_model)

    return models_with_params


def permute_params_for_nonzero(params, n_nonzero):
    return itertools.product(params, repeat=n_nonzero)


