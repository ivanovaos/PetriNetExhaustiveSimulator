__author__ = "Olga Ivanova"
__date__ = "26.07.2016"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"

#Python 3.3.2

import configparser

dict = {"TR": "Test run",
        "PS": "Pipeline settings",
        "MGPS": "Model gen python settings",
        "MGRS": "Model gen R settings",
        "MW": "Model writer",
        "L": "Logging",
        "M": "Model",
        "S": "Simulation"}


class Config:

    def __init__(self, configfile="pipeline_config.conf"):
        self.config = configparser.RawConfigParser()
        self.data = {}
        self.parse_config_file(configfile)

    def parse_config_file(self, configfile):
        self.config.read(configfile)

        if self.is_test_run():
            self.data["models"] = self.getint(dict["TR"], "n_models")
            self.data["folder"] = self.get(dict["TR"], "folder")
            self.set_pipeline()
            self.set_logging()
            self.set_simulation()

        else:
            self.set_pipeline()
            self.set_logging()
            self.set_simulation()

    def is_test_run(self):
        m = dict["TR"]
        self.data["test"] = self.getb(m, "test")
        return self.data["test"]

    def set_pipeline(self):
        m = dict["PS"]
        self.data["model_generating"] = self.getb(m, "model_generating")
        self.data["mg_lang"] = self.get(m, "model_gen_lang")
        self.data["simulate"] = self.getb(m, "simulate")
        self.data["log_silenced"] = self.getb(m, "silence_log")

        if self.data["model_generating"]:
            if self.data["mg_lang"] in ("python", "py", "p"):
                self.set_model_gen_python()
            if self.data["mg_lang"] in ("R", "r"):
                self.set_model_gen_R()

    def set_model_gen_python(self):
        m = dict["MGPS"]
        self.data["is_write_topologies"] = self.getb(m, "write_topologies")
        self.data["is_write_models"] = self.getb(m, "write_models")
        self.set_model_writer()

    def set_model_gen_R(self):
        self.data["sh_file"] = self.get(dict["MGRS"], "sh_file")

    def set_model_writer(self):
        if self.data["is_write_topologies"] or self.data["is_write_models"]:
            m = dict["MW"]

            self.data["folder_topologies"] = self.get(m, "folder_topologies")
            self.data["folder_models"] = self.get(m, "folder_models")

            self.data["one_file_topologies"] = self.getb(m, "one_file_topologies")
            self.data["n_models_per_file"] = self.getint(m, "n_models_per_file")

    def set_logging(self):
        m = dict["L"]

        if self.data["log_silenced"]:
            self.data["log_lvl_console"] = "e"
            self.data["log_lvl_file"] = "e"
        else:
            self.data["log_lvl_console"] = self.get(m, "log_level_console")
            self.data["log_lvl_file"] = self.get(m, "log_level_file")


    def set_simulation(self):
        m = dict["S"]
        self.data["run_one_by_one"] = self.getb(m, "run_one_by_one")

        if self.data["simulate"]:
            if not self.data["run_one_by_one"]:
                self.data["folder_models"] = self.get(m, "folder_models")

            self.data["simulation_folder"] = self.get(m, "simulation_folder")
            self.data["n_pn_per_file"] = self.getint(m, "n_pnets_per_file")
            self.data["simplified_format"] = self.getb(m, "simplified_format")
            self.data["tokens"] = self.getint(m, "tokens")
            self.data["num_sim"] = self.getint(m, "num_sim")
            self.data["num_steps"] = self.getint(m, "num_steps")
            self.data["file_petrinets"] = self.getb(m, "file_petrinets")

    def get(self, m, name):
        return self.config.get(m, name)

    def getb(self, m, name):
        return self.config.getboolean(m, name)

    def getint(self, m, name):
        return self.config.getint(m, name)

    # Returns -1 if there is no such attribute
    def __getitem__(self, item):
        if item in self.get_all_attributes():
            return self.data[item]
        return -1

    def get_all_attributes(self):
        return self.data.keys()

    def __str__(self):
        return " ".join([s + ":" + str(k) + "\n" for s, k in self.data.items()])