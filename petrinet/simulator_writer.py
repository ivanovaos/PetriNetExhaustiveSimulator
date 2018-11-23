__author__ = "Olga Ivanova"
__date__ = "1.08.2016"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"
# minor update = "Saman Amini"
# Python 3.3.2
import os


class SimulatorWriter:

    n_per_file = 1
    current_file_res = ""
    current_record = 0
    sim_folder = "results/"
    extension = ".txt"
    id = 0
    simplified = True

    def __init__(self):
        pass

    @staticmethod
    def set_sim_folder(folder):
        if not os.path.isdir(folder):
            os.makedirs(folder)
        SimulatorWriter.sim_folder = folder

    @staticmethod
    def reset_id():
        SimulatorWriter.id = 0

    @staticmethod
    def set_n_per_file(n):
        SimulatorWriter.n_per_file = n

    @staticmethod
    def set_writing_format(is_simplified):
        SimulatorWriter.simplified = is_simplified

    @staticmethod
    def write_results_one_petrinet(f, pn, pn_state_collector, mutant):
        model = pn.get_model()

        f.write(model.get_multistring_model_repr())
        SimulatorWriter.add_new_string(f)

        f.write(str(model.get_connections()))
        SimulatorWriter.add_new_string(f)

        st = pn_state_collector.get_printable_average(mutant)
        f.write(st)
        f.write("--------------------------")
        SimulatorWriter.add_new_string(f)

    @staticmethod
    def start_new_record(filename):
        path = SimulatorWriter.sim_folder
        os.makedirs(os.path.dirname(path), exist_ok=True)
        f = open(path + filename + SimulatorWriter.extension, "w+")
        SimulatorWriter.current_file_res = f
        return f

    @staticmethod
    def close_record():
        if not SimulatorWriter.current_file_res.closed:
            SimulatorWriter.current_file_res.close()

    @staticmethod
    def write_results(pnsc):

        current_record = SimulatorWriter.current_record
        n_pn_per_file = SimulatorWriter.n_per_file

        if len(pnsc) > n_pn_per_file:
            for i in range(0, int(len(pnsc)/n_pn_per_file) + 1):
                SimulatorWriter.write_results(pnsc[i * n_pn_per_file: (i + 1) * n_pn_per_file])
        else:

            if not current_record:

                SimulatorWriter.id += 1
                filename = str(SimulatorWriter.id)

                SimulatorWriter.start_new_record(filename)

            if (current_record + len(pnsc)) >= n_pn_per_file:
                diff = n_pn_per_file - current_record

                if SimulatorWriter.simplified:
                    SimulatorWriter.write_simplified_petrinets(pnsc[:diff])
                else:
                    SimulatorWriter.write_extended_results(pnsc[:diff])

                #SimulatorWriter.write_simplified_petrinets(pnsc[:diff])

                SimulatorWriter.close_record()
                SimulatorWriter.current_record = 0

                if len(pnsc) > diff:

                    SimulatorWriter.id += 1
                    filename = str(SimulatorWriter.id)

                    SimulatorWriter.start_new_record(filename)

                    if SimulatorWriter.simplified:
                        SimulatorWriter.write_simplified_petrinets(pnsc[diff:])
                    else:
                        SimulatorWriter.write_extended_results(pnsc[diff:])

                    SimulatorWriter.current_record += len(pnsc[diff:])

            else:
                if SimulatorWriter.simplified:
                    SimulatorWriter.write_simplified_petrinets(pnsc)
                else:
                    SimulatorWriter.write_extended_results(pnsc)
                SimulatorWriter.current_record += len(pnsc)


    @staticmethod
    def write_simplified_petrinets(petrinets_scs):

        f = SimulatorWriter.current_file_res

        for p in petrinets_scs:

            pn = p.petrinet

            f.write(str(pn.id))

            f.write(";incoming: ")
            arc_in_str = SimulatorWriter.get_transitions_str(pn.WT_weights_in)
            f.write(arc_in_str)

            f.write(" outgoing: ")
            arc_out_str = SimulatorWriter.get_transitions_str(pn.WT_weights_out)
            f.write(arc_out_str)

            SimulatorWriter.add_delimeter(f)

            results = []
            for mutant in p.gel_all_mutants_sorted():
                results.append(p.get_last_values_genes(mutant))

            f.write(SimulatorWriter.get_results_str(results))
            SimulatorWriter.add_new_string(f)

        #SimulatorWriter.add_new_string(f)

    @staticmethod
    def write_extended_results(petrinets_scs):

        f = SimulatorWriter.current_file_res

        for p in petrinets_scs:

            pn = p.petrinet

            f.write(str(pn.id))
            SimulatorWriter.add_new_string(f)

            f.write("incoming: ")
            arc_in_str = SimulatorWriter.get_transitions_str(pn.WT_weights_in)
            f.write(arc_in_str)

            SimulatorWriter.add_new_string(f)
            f.write("outgoing: ")
            arc_out_str = SimulatorWriter.get_transitions_str(pn.WT_weights_out)
            f.write(arc_out_str)

            results = []
            for mutant in p.gel_all_mutants_sorted():
                results.append(p.get_printable_average(mutant))
                #TODO
                #results.append(p.get_transitions_fired(mutant))

            SimulatorWriter.add_new_string(f)
            f.write(SimulatorWriter.get_results_str_extended(results))

            SimulatorWriter.add_new_string(f)

    @staticmethod
    def get_transitions_str(transitions):
        return " ".join([str(t) + ":" + str(v) for t, v in sorted(transitions.items())])

    @staticmethod
    def get_results_str(res):
        return ":".join([str(r[0]) + " " + str(r[1]) for r in res])

    @staticmethod
    def get_results_str_extended(res):
        return "\n".join(r for r in res)

    @staticmethod
    def add_delimeter(f):
        f.write(";")

    @staticmethod
    def add_new_string(f, n=1):
        for i in range(0, n):
            f.write("\n")
