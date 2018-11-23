#!/usr/bin/python
# Script to simulate Petri nets
# Made by Annika Jacobsen 2014
# Updated by Maxim Monait 2015
# Updated by Annika Jacobsen 2016
# Updated by Olga Ivanova 2016

import argparse
import itertools
import logging

from model.model import Model

from petrinet.petrinet_generator import PNGenerator
from petrinet.petrinet_state_collector import PNStateCollector
from model.model_checker import ModelChecker

from copy import deepcopy


class PetriNetSimulator:

    def __init__(self):
        pass

    def set_simulator(self, num_sim, num_steps, tokens):
        self.num_sim = num_sim
        self.num_steps = num_steps
        self.tokens = tokens

    # MULTIPLE SIMULATIONS
    def multi_sim(self, p, pn_state_collector, num_sim):
        mutant = p.get_mutant_str()
        logging.debug("Simulations for the petrinet: " + str(num_sim))

        for i in range(0, num_sim):
            p.reset_petri_net()
            self.single_sim(p, pn_state_collector, i)

        logging.debug("\n" + pn_state_collector.get_printable_average(mutant))

    # SINGLE SIMULATION
    def single_sim(self, p, pn_state_collector, run_id):
        transitions_fired = []
        mutant = p.get_mutant_str()

        for i in range(0, self.num_steps):
            state = p.get_current_state()
            pn_state_collector.store_step(mutant, state, run_id)

            # Do one step of the simulation
            trans_f = p.single_step()
            transitions_fired.append(trans_f)

        last_state = p.get_current_state()
        pn_state_collector.store_step(mutant, last_state, run_id, transitions_fired)


    # MULTIPLE INITIAL STATES
    def multi_init_states(self, p):
        token_value = self.tokens
        iter_combinations = itertools.product([0, token_value], repeat=2)

        base_model = Model.deepcopy_model(p.get_model())
        #TODO deepcopy was added on the debugging step, WT instead?
        transitions = [deepcopy(p.arc_weights_in), deepcopy(p.arc_weights_out)]

        pn_sc = PNStateCollector(p)
        num_sim = self.calculate_number_simulation(p)
        changed_model = False

        for places_init in sorted(iter_combinations, reverse=True):
            model = base_model

            regulators_correction = ModelChecker.regulators_connected(base_model)
            pl_in = places_init

            #TODO magic numbers should go; magic strings as well
            if (len(regulators_correction) == 1) and ("R1", "R2") in regulators_correction.keys():
                pl_in = (places_init[0], 0)
            elif (len(regulators_correction) == 1) and ("R2", "R1") in regulators_correction.keys():
                pl_in = (0, places_init[1])
            elif (len(regulators_correction) == 2) and all(value < 0 for value in regulators_correction.values()):
                pl_in = (0, 0)
            elif (len(regulators_correction) == 2) and regulators_correction[("R1", "R2")] < 0:
                pl_in = (places_init[0], 0)
            elif (len(regulators_correction) == 2) and regulators_correction[("R2", "R1")] < 0:
                pl_in = (0, places_init[1])

            model = self.delete_dead_connections(places_init, base_model)

            if not ModelChecker.same_model(model, base_model):
                logging.debug("Model updated: " + str(model))
                p = PNGenerator.load_pn_model(model, p.id, transitions, places_init, changed=True)
                changed_model = True
            elif changed_model:
                #if model has been changed on the previous step, load petri net again
                p = PNGenerator.load_pn_model(model, p.id, transitions, places_init)

            p.set_mutant_str(places_init)
            p.set_initial_state(pl_in)

            logging.debug("Mutant: " + str(p.get_mutant_str()))

            self.multi_sim(p, pn_sc, num_sim)

        return pn_sc


    def calculate_number_simulation(self, petrinet):
        num_sim = 1
        invariable_runs = petrinet.is_variable_runs()
        # If petrinet doesn't have competitive arcs, run only once
        if invariable_runs == 1:
            num_sim = 10
        elif invariable_runs > 1:
            num_sim = 100
        return num_sim

    # Deletes incoming connections if regulator is off, so it won't get tokens
    def delete_dead_connections(self, places_init, base_model):

        model = Model.deepcopy_model(base_model)
        for mut, place in zip(places_init, ['R1', 'R2']):
            #TODO change R1 and R2 to regulators
            if mut == 0:
                model.reset_incoming_connection(place)
        return model


#TODO rewrite the example according to refactored code
def run_example_model():
    places = {"R1": 4, "R2": 4, "G1": 0, "G2": 0} #first state for all models

    transitions = ["t1", "t2", "t3"]
    arc_weights_in = {
        "t1": {"R1": 1},
        "t2": {"R1": -1, "R2": -1},
        "t3": {"G2": 1}}

    arc_weights_out = {
        "t1": {"G1": 1},
        "t2": {"G2": 1},
        "t3": {"G1": 5}}

    #test the different rules for transition. Use pnSim.run_alternative_model()
    #places = {"in": 0, "out": 0}
    #transitions = ["t1"]
    #arc_weights_in = {"t1": {"in": -1}}
    #arc_weights_out = {"t1": {"out": 1}}

    #places = {"in1": 0, "in2": 0, "out": 0}
    #transitions = ["t1"]
    #arc_weights_in = {"t1": {"in1": -1, "in2": -1}}
    #arc_weights_out = {"t1": {"out": 1}}

    pnSim.set_petri_net_model(transitions, places, arc_weights_in, arc_weights_out ) #MM 24-08-2015


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a Petri net simulation tool')
    parser.add_argument('-i', '--infile', help='input file of all the models', required=False)
    args = vars(parser.parse_args())

    pnSim = PetriNetSimulator()
    pnSim.set_simulator(num_sim=1, num_steps=4, tokens=4)

    if not args['infile']:
        run_example_model()

    else:
        #TODO
        filename = "sample_models/input_model3.txt"
        pnSim.simulate_one_model(filename)