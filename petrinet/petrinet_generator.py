__author__ = "Olga Ivanova"
__date__ = "01.08.2016"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"

# Python 3.3.2
import itertools

from .petrinet import PetriNet
from model.model_handler import ModelHandler
from copy import deepcopy


class PNGenerator:

    def __init__(self):
        pass

    @staticmethod
    def generate_pns_file(filename):
        pn_array = []
        model = ModelHandler.read_model_file(filename)
        options = PNGenerator.generate_pn_options(model)

        for idx, transitions in enumerate(options):
            id = str(model) + str(idx)
            p = PetriNet.load_petrinet_model(model, id, transitions)
            pn_array.append(p)

        return pn_array

    @staticmethod
    def generate_pns_model(model, option=-1):
        pn_array = []
        options = PNGenerator.generate_pn_options(model)

        if option == -1:
            for idx, transitions in enumerate(options):
                id = str(model) + "_" + str(idx + 1)
                p = PetriNet.load_petrinet_model(model, id, transitions)
                pn_array.append(p)
        else:
            for idx, transitions in enumerate(options):
                if idx == option-1:
                    id = str(model) + "_" + str(idx + 1)
                    p = PetriNet.load_petrinet_model(model, id, transitions)
                    pn_array.append(p)

        return pn_array


    @staticmethod
    def load_pn_model(model, id, transitions, places_init, changed=False):
        updated_trans = transitions
        if changed:
            updated_trans = PNGenerator.reset_unused_transitions(model, transitions)
        return PetriNet.load_petrinet_model(model, id, updated_trans, places_init)

    @staticmethod
    def generate_pn_options(model):
        connections = model.get_connections_combined()
        n = sum(1 for v in connections.values() if len(v) > 1)
        n_petri = itertools.product((1, 2), repeat=n)

        pn_options = []

        for opt in n_petri:
            option = PNGenerator.generate_transition_option(connections, opt)

            if option:
                pn_options.append(option)

        return pn_options

    @staticmethod
    def reset_unused_transitions(model, transitions):
        transitions_out_new = {}

        transitions_in = deepcopy(transitions[0])
        transitions_out = deepcopy(transitions[1])

        connections = model.get_connections_combined()

        for trans, value in transitions_out.items():
            if list(value.keys())[0] in list(connections.keys()):
                transitions_out_new[trans] = value
            #else:
            #    transitions_in.pop(trans, None)

        return [transitions_in, transitions_out_new]


    @staticmethod
    def generate_transition_option(connections, option):
        weights = {1: [1, 1], 5: [1, 5], -1: [-1, 1], -5: [-1, 5]}

        n_trans = 1
        tran_in = {}
        tran_out = {}
        op = 0

        for c_out, c_in in sorted(connections.items()):

            if len(c_in.keys()) > 1:

                #OR
                if option[op] == 1:

                    for c, k in sorted(c_in.items()):
                        value = k
                        PNGenerator.update_transitions(tran_in, tran_out, {c: value}, c_out, value, n_trans)
                        n_trans += 1

                #AND
                elif option[op] == 2:

                    #TODO comment it
                    w = [weights[i][1] for i in c_in.values()]
                    #TODO change to if all of the values are not equal
                    if w[0] != w[1]:
                        return []

                    for c, k in sorted(c_in.items()):
                        value = k
                        PNGenerator.update_transitions(tran_in, tran_out, {c: value}, c_out, value, n_trans)

                    n_trans += 1

                op += 1

            else:
                value = list(c_in.values())[0]
                PNGenerator.update_transitions(tran_in, tran_out, c_in, c_out, value, n_trans)
                n_trans += 1

        return [tran_in, tran_out]

    #TODO think about static and logic
    @staticmethod
    def update_transitions(tran_in, tran_out, c_in, c_out, value, n_trans):
        weights = {1: [1, 1], 5: [1, 5], -1: [-1, 1], -5: [-1, 5]}

        t_name = "t" + str(n_trans)
        #TODO change it
        c_in = list(c_in.keys())[0]

        #TODO update or create
        if t_name in tran_in.keys():
            tran_in[t_name].update({c_in: weights[value][0]})
            tran_out[t_name].update({c_out: weights[value][1]})
        else:
            tran_in[t_name] = {c_in: weights[value][0]}
            tran_out[t_name] = {c_out: weights[value][1]}

        return [tran_in, tran_out]