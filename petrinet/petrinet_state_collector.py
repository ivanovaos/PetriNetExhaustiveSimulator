__author__ = "Olga Ivanova"
__date__ = "30.07.2016"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"

import numpy as np

#TODO transfer through the __init__
places_default = ["R1", "R2", "G1", "G2"]
genes = ["G1", "G2"]

class PNStateCollector:

    def __init__(self, p, places=places_default):
        #TODO do we need to keep petrinet itself here?
        self.petrinet = p
        self.sim = {}
        self.places = places
        #TODO tmp measure
        self.transitions_fired = {}

    def add_mutant(self, mutant):
        self.sim[mutant] = {}

        keys = self.places
        for k in keys:
            self.sim[mutant][k] = []

    def get_all_mutants(self):
        return self.sim.keys()

    def gel_all_mutants_sorted(self):
        return sorted(self.sim.keys(), reverse=True)

    def store_step(self, mutant, dict, run_id, transitions_fired=[]):
        if mutant not in self.sim.keys():
            self.add_mutant(mutant)

        for place, value in dict.items():
            step = self.get_step_array(mutant, place, run_id)
            step.append(value)

        if transitions_fired:
            if mutant not in self.transitions_fired.keys():
                self.transitions_fired[mutant] = {}
            self.transitions_fired[mutant] = transitions_fired

    def get_mutant_place(self, mutant, place):
        return self.sim[mutant][place]

    def get_step_array(self, mutant, place, run_id):
        mutant_place = self.get_mutant_place(mutant, place)
        if run_id == len(mutant_place):
            mutant_place.append([])
        return mutant_place[run_id]

    def get_transitions_fired(self, mutant):
        return self.transitions_fired[mutant]

    def get_printable_average(self, mutant):
        means = self.calculate_average_per_mutant(mutant)
        mean_str = ""

        for k in places_default:
            val = " ".join(str(s) for s in means[k])
            mean_str += k + " " + val + "\n"

        return mean_str

    def calculate_average_per_mutant(self, mutant):
        mutant_data = self.sim[mutant]
        means = {}
        for k, v in mutant_data.items():
            means[k] = np.mean(np.array(v), axis=0)

        return means

    #TODO store means for mutants?
    def get_last_values_genes(self, mutant):
        mean = self.calculate_average_per_mutant(mutant)
        #get last values for G1 and G2 from petri net firing
        return mean["G1"][-1], mean["G2"][-1]