#!/usr/bin/env python

__author__ = "Olga Ivanova"
__date__ = "26.07.2016"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"

#Python 3.3.2

import logging
import os
import fnmatch
import shutil
import getopt
import sys
import subprocess
import glob
from logging.handlers import RotatingFileHandler
import cProfile, pstats, io

import model.model_generator as mod_gen
from model.model_handler import ModelHandler
from config_reader import Config
from petrinet.petrinet_simulator import PetriNetSimulator
from petrinet.petrinet_generator import PNGenerator
from petrinet.simulator_writer import SimulatorWriter
from petrinet.petrinet_reader import PetrinetReader

class Pipeline:

    def run_python_model_generator(self, t_folder, m_folder, is_write_topology=False, is_write_models=False,
                                   is_generate_models=False, n_models_per_file=5000):

        if is_write_topology:
            self.clean_models_folder(t_folder)
        if is_write_models:
            self.clean_models_folder(m_folder)

        topologies = mod_gen.generate_filtered_topologies(t_folder, is_write_topology)

        if is_generate_models:
            ModelHandler.set_path(m_folder)
            ModelHandler.set_n_per_file(n_models_per_file)

            models_with_params = mod_gen.generate_models_with_parameters(topologies, m_folder, is_write_models)

            n_models = sum([len(models_with_params[m]) for m in models_with_params])
            logging.info("Generated number of models " + str(n_models))

            return models_with_params

        return topologies

    def run_R_model_generator(self, sh_file):
        subprocess.call([sh_file])

    def run_sim_generating_m(self, pnSim, conf, n_models=-1):
        topologies = mod_gen.generate_filtered_topologies(is_write=False)
        #TODO add possibility to write models to files
        self.generate_and_simulate_models(topologies, pnSim, n_models, conf)

    def generate_and_simulate_models(self, topologies, pnSim, n_models, conf):
        #TODO clean result folder every time? Create new folder?
        self.clean_models_folder(conf["simulation_folder"])

        models_with_params = {}
        n_expected = 0
        n_generated = 0
        n_petrinets = 0

        logging.info("Simulation has started...")

        for idx, topology in enumerate(topologies):
            topology_str = str(topology)

            logging.info("Generating permutations of all parameters for topology #" + str(idx))
            logging.debug("\n" + topology.get_multistring_model_repr())

            n_expected_current = mod_gen.calculate_n_of_models(topology.get_connection_num(), 4)
            logging.debug("Expected number of models for topology #" + str(idx) + ": " + str(n_expected_current))

            n_expected += n_expected_current
            new_models = mod_gen.generate_models_for_topology(topology)
            models_with_params[topology_str] = new_models

            if n_models != -1 and (n_generated + len(new_models)) >= n_models:
                updated_n = int(n_models - n_generated)
                new_models = new_models[0:updated_n]
                n_expected = n_models

                n_petrinets += self.run_simulation(pnSim, n_generated, models=new_models)
                n_generated += updated_n
                break

            else:
                n_petrinets += self.run_simulation(pnSim, n_generated, models=new_models)
                n_generated += len(models_with_params)

            logging.info("Generating finished, n models " + str(len(new_models)) + " topology #" + str(idx))

        SimulatorWriter.close_record()


        logging.info("Generating has been finished for all of the models")
        logging.info("Expected number of models: " + str(n_expected))
        logging.info("Generated number of models " + str(n_generated))
        logging.info("Simulated petrinets: " + str(n_petrinets))
        logging.info("Simulation has been finished for all the models")


    def run_simulation_folder(self, pnSim, models_folder, output_folder, file_petrinets=False):

        n_petrinets = 0

        files = []
        for f in os.listdir(models_folder):
            if os.path.isfile(models_folder + f) and fnmatch.fnmatch(f, "*.txt"):
                files.append(f)

        logging.info("Simulation has started...")

        models = []
        n_models = 0

        self.clean_models_folder(SimulatorWriter.sim_folder)
        SimulatorWriter.reset_id()

        for f in files:
            logging.info("Simulating model file: " + f)
            if file_petrinets:
                models = PetrinetReader.read_petrinet(models_folder + f)
            else:
                models = ModelHandler.read_models_from_file(models_folder + f)

            if models:
                n_petrinets += self.run_simulation(pnSim, n_models, models, output_folder, file_petrinets)
                n_models += len(models)

        if files:
            SimulatorWriter.close_record()

        logging.info("Simulated number of models: " + str(n_models))
        logging.info("Simulated petrinets: " + str(n_petrinets))
        logging.info("Simulation has been finished for all the models")

    def run_simulation(self, pnSim, n_models, models=[], output_folder="", file_petrinets=False):

        n_petrinets = 0

        if file_petrinets:
             for idx, data in enumerate(models.keys()):
                petrinets = self.simulate_one_model(pnSim, n_models + idx + 1, model=data,
                                                    pn_option=models[data])

                if petrinets:
                    try:
                        SimulatorWriter.write_results(petrinets)
                    except:
                        logging.error("Failed to write results of simulation for model: " + str(data))
                        logging.error(sys.exc_info())
                        logging.error(sys.exc_info())
                    n_petrinets += len(petrinets)

        else:
            for idx, data in enumerate(models):
                petrinets = self.simulate_one_model(pnSim, n_models + idx + 1, model=data)

                if petrinets:
                    try:
                        SimulatorWriter.write_results(petrinets)
                    except:
                        logging.error("Failed to write results of simulation for model: " + str(data))
                        logging.error(sys.exc_info())
                        logging.error(sys.exc_info())
                    n_petrinets += len(petrinets)

        return n_petrinets

    def simulate_one_model(self, pnSim, model_n, model, pn_option=-1):

        logging.info("Simulating model N " + str(model_n) + ": " + str(model))

        pns = PNGenerator.generate_pns_model(model, pn_option)
        pnSC = []

        for idx, p in enumerate(pns):
            logging.debug("Petrinet: " + str(idx + 1))
            logging.debug("Incoming arcs: " + str(p.arc_weights_in))
            logging.debug("Outgoing arcs: " + str(p.arc_weights_out))

            try:
                results = pnSim.multi_init_states(p)
                pnSC.append(results)
            except:
                logging.error("Simulation failed for petrinet " + str(p.id))
                logging.error(sys.exc_info())

        logging.info("Simulating model " + str(model) + " finished")
        return pnSC

    def clean_models_folder(self, folder):

        logging.info("Cleaning folder for models: %s", folder)

        if os.path.exists(folder):
            filelist = glob.glob(folder + "*.txt")

            for f in filelist:
                os.remove(f)
        else:
            logging.info("There is no folder with the name %s. Nothing to be cleaned.", folder)

    def add_logging(self, log_level_file, log_level_console, output_folder=""):

        lvl_basic = self.get_log_level_from_str(log_level_file)

        root_logger = logging.getLogger()
        root_logger.setLevel(level=logging.DEBUG)

        file_logger = RotatingFileHandler(filename=SimulatorWriter.sim_folder + "pipeline.log",
                                          maxBytes=50*1024*1024, backupCount=50, mode='wr+')
        file_logger.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt="%I:%M:%S %p"))
        file_logger.setLevel(level=lvl_basic)

        root_logger.addHandler(file_logger)

        console_logger = self.set_logging_console(log_level_console)
        root_logger.addHandler(console_logger)

    def set_logging_console(self, level):
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console_logger = logging.StreamHandler()
        console_logger.setLevel(self.get_log_level_from_str(level))
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console_logger.setFormatter(formatter)
        return console_logger

    def get_log_level_from_str(self, level):
        if level in ("debug", "d"):
            return logging.DEBUG
        elif level in ("info", "i"):
            return logging.INFO
        elif level in ("error", "e"):
            return logging.ERROR
        elif level in ("critical", "c"):
            return logging.CRITICAL

    def test_run(self, pnSim, folder, n_models):
        logging.info("This is test run, folder: " + folder + "number of models: " + str(n_models))

        if folder:
            self.run_simulation_folder(pnSim, folder)
        else:
            self.run_sim_generating_m(pnSim, n_models=n_models)

    def production_run(self, conf, pnSim, output_folder, dir=""):

        if conf["run_one_by_one"] and conf["simulate"]:
            self.run_sim_generating_m(pnSim)

        else:
            if conf['model_generating']:
                if conf["mg_lang"] in ("R", "r"):
                    self.run_R_model_generator(conf["sh_file"])
                else:
                    self.run_python_model_generator(conf['folder_topologies'], conf['folder_models'],
                                               conf['is_write_topologies'], conf['is_write_models'],
                                               conf['is_generate_models'], conf["n_models_per_file"])

            if conf["simulate"]:
                if dir:
                    self.run_simulation_folder(pnSim, dir, output_folder, conf["file_petrinets"])
                else:
                    self.run_simulation_folder(pnSim, conf["folder_models"], output_folder,
                                               conf["file_petrinets"])


    def init_setup(self, conf, output_folder=""):
        pnSim = PetriNetSimulator()
        pnSim.set_simulator(conf["num_sim"], conf["num_steps"], conf["tokens"])

        SimulatorWriter.set_n_per_file(conf["n_pn_per_file"])
        SimulatorWriter.set_sim_folder(conf["simulation_folder"] + output_folder)
        SimulatorWriter.set_writing_format(conf["simplified_format"])

        return pnSim

    #TODO change it to the new parser
    def define_script_params(self, argv):

        config_file, dir, output_folder = "", "", ""

        try:
            opts, args = getopt.getopt(argv, "hc:d:o:", ["config=", "dir=", "output="])
        except getopt.GetoptError:
            logging.error("pipeline.py -c <config_file> -d <models_dir> -o <output_folder> -h")
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                logging.info("pipeline.py -c <config_file> -d <models_dir> -o <output_folder> -h")
                sys.exit()
            elif opt in ("-c", "--config"):
                config_file = arg
            elif opt in ("-d", "--dir"):
                dir = arg
            elif opt in ("-o", "--output"):
                output_folder = arg

        return {"config_file": config_file, "dir": dir, "output_folder": output_folder}

    def start(self, argv):
        params = self.define_script_params(argv[1:])
        config_file = params["config_file"]

        if params["dir"]:
            dir = params["dir"]

        output_folder = params["output_folder"]

        conf = Config(config_file)
        pnSim = self.init_setup(conf, output_folder)
        self.add_logging(conf["log_lvl_file"], conf["log_lvl_console"], output_folder)

        # Rename simulation folder to different name
        logging.info("Config file: " + config_file)

        if dir:
            logging.info(" Models directory: " + str(dir))
        logging.info("Set up: \n" + str(conf))


        if conf["test"]:
            #TODO in test run: run only n first models from folder
            self.test_run(pnSim, conf["folder"], conf["models"])
        else:
            self.production_run(conf, pnSim, output_folder, dir)

        #TODO this was for profiling and we probably don't need to improve simulation time anymore
        # else:
        #     pr = cProfile.Profile()
        #     pr.enable()
        #
        #     production_run(pnSim, dir)
        #
        #     s = io.StringIO()
        #     pr.disable()
        #     sortby = "cumulative"
        #     ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        #     ps.print_stats()
        #     print(s.getvalue())

if __name__ == '__main__':
    pipeline = Pipeline()
    pipeline.start(sys.argv)



