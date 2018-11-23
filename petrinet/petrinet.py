# Made by Annika Jacobsen 2014
# Updated by Maxim Monait 2015
# Updated by Annika Jacobsen 2016
# Updated by Olga Ivanova 2016

from copy import deepcopy
import copy
import numpy as np

from model.model_checker import ModelChecker
from model.model import Model

#TODO
places_t_default = {"R1": 4, "R2": 4, "G1": 0, "G2": 0}
places = ["R1", "R2", "G1", "G2"]

class PetriNet:

    def __init__(self):
        pass

    @classmethod
    def load_petrinet_model(cls, model, id, transitions, place_init=places_t_default):
        p = PetriNet()
        p.model = Model.deepcopy_model(model)
        p.build_petri_net(id, transitions, place_init)
        return p

    def get_model(self):
        return self.model

    def build_petri_net(self, id, transitions, places_init=places_t_default):
        self.id = id
        self.set_initial_state(places_init)
        self.transitions = list(transitions[0].keys())
        self.arc_weights_in = transitions[0]
        self.arc_weights_out = transitions[1]

        #TODO think carefully how to do that in a nicer way
        self.WT_weights_in = deepcopy(transitions[0])
        self.WT_weights_out = deepcopy(transitions[1])

    def is_variable_runs(self):
        return ModelChecker.has_competing_connections(self.get_model())

    def reset_petri_net(self):
        self.places_tokens = deepcopy(self.places_init)

    def set_mutant_str(self, values):
        st = []

        for k in values:
            if k == 0:
                st.append(0)
            else:
                st.append(1)

        self.mutant = "".join(str(v) for v in st)[0:2]

    def get_mutant_str(self):
        return self.mutant

    # These initial states correspond to gene deletions. This means that we should never get
    # tokens to deleted genes(regulators), it does not make sense anyway because they are deleted.
    # With the current setup depending on incoming edges to regulators there is still a chance that
    # they get tokens. The way to deal with this is to remove all incoming activating edges to the deleted gene.
    #TODO
    def set_initial_state(self, values):
        self.places_init = {}

        if values == places_t_default:
            self.places_init = places_t_default

        else:
            self.places_init["R1"] = values[0]
            self.places_init["R2"] = values[1]
            self.places_init["G1"] = 0
            self.places_init["G2"] = 0

    # SINGLE STEP
    def single_step(self):

        transitions_fired = [];
        places_temp = deepcopy(self.places_tokens)  # used to check whether a transition is valid.

        transitions_rand = copy.copy(self.transitions)

        # all enabled transitions are fired in each step
        while len(transitions_rand) > 0:

            t = self.get_transition_randomly(transitions_rand)
            transition_valid = self.check_transition_validity(t, places_temp)

            if len(self.arc_weights_in[t].values()) == 2:  # if there are two incoming arcs
                transition_valid = self.choose_winner(t, places_temp, transition_valid)

            # fires transition if requirement(s) are valid
            if transition_valid:
                transitions_f = self.fire_transition(t, places_temp)
                transitions_fired += transitions_f

        return transitions_fired


    def check_transition_validity(self, t, places_t):
        transition_valid = True

        transition = self.arc_weights_in[t]
        # check if requirement(s) to fire transition are FALSE, otherwise assumed TRUE (valid)
        for p in transition:
            # for inhibitory arcs
            if transition[p] < 0 and places_t[p] > 0:
                transition_valid = False
            # for activating arcs
            elif (transition[p] > 0) and not (places_t[p] - transition[p] >= 0):
                transition_valid = False

        return transition_valid

    def fire_transition(self, t, places_temp):
        transitions_fired = []

        transition = self.arc_weights_in[t]

        for p in transition:
            # only consume from an activating place if tokens are present.
            # (Transitions can fire from an empty activating input place
            # if another empty inhibitory input place exists)
            if transition[p] > 0 and places_temp[p] > 0:
                places_temp[p] = places_temp[p] - transition[p]
                self.update_place_token(p, -transition[p])

                transitions_fired.append(p)

        if t in self.arc_weights_out:
            for p in self.arc_weights_out[t]:
                self.update_place_token(p, self.arc_weights_out[t][p])

        return transitions_fired

    def update_place_token(self, place, value):
        self.places_tokens[place] += value

    # Inhibition wins over activation if there is a conflict
    def choose_winner(self, t, places_t, transition_valid):
        transition_valid = transition_valid
        transition = self.arc_weights_in[t]

        # we are expecting only arc with the same value modulo here
        if sum(transition.values()) == 0:  # activating and inhibiting arcs
            for p in transition:
                if transition[p] < 0 and places_t[p] == 0:  # if the inhibiting arc is valid
                    transition_valid = True

        return transition_valid

    def get_transition_randomly(self, transitions_rand):
        random_int = np.random.randint(0, len(transitions_rand))  # better than random.shuffle (#MM 28-08-2015)
        return transitions_rand.pop(random_int)

    def get_current_state(self):
        return self.places_tokens

