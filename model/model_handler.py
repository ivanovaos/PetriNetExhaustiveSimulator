__author__ = "Olga Ivanova"
__date__ = "28.07.2016"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"


# TODO singleton
from .model import Model
import logging
import os
import sys
import re


class ModelHandler:

    path = ""
    n_per_file = 1000
    current_file = ""
    current_record = 0

    def __init__(self):
        pass

    @staticmethod
    def set_path(path):
        ModelHandler.path = path

    @staticmethod
    def set_n_per_file(n):
        ModelHandler.n_per_file = n


    @staticmethod
    def start_new_record(filename):
        path = ModelHandler.path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        f = open(path + filename + ".txt", "w+")
        ModelHandler.current_file = f
        return f

    @staticmethod
    def close_record():
        if not ModelHandler.current_file.closed:
            ModelHandler.current_file.close()


    @staticmethod
    def write_models_to_file(models, is_model=True, topology_str="", update_percent=0.25):

      #  if is_model:
      #      ModelWriter.path = ModelWriter.path + topology_str + "/"
      #  os.makedirs(os.path.dirname(ModelWriter.path), exist_ok=True)

       # percent_complete = 0
       # n_matrices = 0

        current_record = ModelHandler.current_record
        n_per_file = ModelHandler.n_per_file

        if len(models) > n_per_file:
            for i in range(0, int(len(models)/n_per_file) + 1):
                ModelHandler.write_models_to_file(models[i * n_per_file: (i + 1) * n_per_file])

        else:
            if not current_record:
                filename = str(models[0])
                ModelHandler.start_new_record(filename)

            if (current_record + len(models)) >= n_per_file:
                diff = n_per_file - current_record
                ModelHandler.write_models(models[:diff])
                ModelHandler.close_record()
                ModelHandler.current_record = 0

                if len(models) > diff:
                    filename = str(models[diff])
                    ModelHandler.start_new_record(filename)
                    ModelHandler.write_models(models[diff:])
                    ModelHandler.current_record += len(models[diff:])

            else:
                ModelHandler.write_models(models)
                ModelHandler.current_record += len(models)


    @staticmethod
    def write_models(models):#, idx_n, n, update_percent):
        f = ModelHandler.current_file
        for m in models:
            f.write(m.get_multistring_model_repr())
            f.write("\n\n")
          #  if (idx_n/n) >= (percent_complete + update_percent):
          #      logging.debug(str(percent_complete * 100) + " percent complete")
          #      percent_complete = idx_n/n

        #return idx_n


    @staticmethod
    def read_model_file(filename):
        try:
            with open(filename, "r") as f:
                lines = f.read().splitlines()
            f.close()

            m = ModelHandler.read_one_model(lines)
        except:
            logging.error("File " + filename + " is not a model file")
            logging.error(sys.exc_info())

        return m

    @staticmethod
    #this method is used for running again interesting models
    def read_models_from_file(filename):
        models = []

        try:
            with open(ModelHandler.path + filename, "r") as f:
                lines = f.read().splitlines()

            i = 0
            #four lines per model + blank line
            while i < len(lines):
                if lines[i] and len(re.split(" |\\t", lines[i])) == 1:
                    model = ModelHandler.read_one_model_line(lines[i])
                elif lines[i]:
                    model_lines = lines[i:i+4]
                    model = ModelHandler.read_one_model(model_lines)
                    i += 4

                i += 1
                if model:
                    models.append(model)
                    model = ""


        except (ValueError, UnicodeDecodeError):
            logging.error("File " + filename + " is not a model file")
            logging.error(sys.exc_info())

        return models

    @staticmethod
    #TODO refactor it
    def read_models_in_line(filename):
        models = []

        try:
            with open(ModelHandler.path + filename, "r") as f:
                lines = f.read().splitlines()
            f.close()

            for i in range(0, len(lines)):
                model = ModelHandler.read_one_model_line(lines[i])
                models.append(model)

            return models

        except (ValueError, UnicodeDecodeError):
            logging.error("File " + filename + " is not a model file")
            logging.error(sys.exc_info())


    @staticmethod
    def read_one_model_line(model_line):
        model_line_splitted = model_line.split("_")[0]
        model = []

        m_line = ""
        for idx, symbol in enumerate(model_line_splitted):
            if symbol.isdigit() and idx != len(model_line_splitted) - 1:
                m_line += symbol + ","
            else:
                m_line += symbol

        model_line_splitted = m_line.split(",")

        try:
            for i in range(0, len(model_line_splitted), 4):
                line = model_line_splitted[i:i+4]
                line = [int(m) for m in line]
                if len(line) != 4:
                    raise TypeError
                model.append(line)

            return Model(model)

        except TypeError:
            logging.error("Model format " + str(model_line) + " is incorrect")


    @staticmethod
    #TODO add check up for corretness of the model
    def read_one_model(lines):
        model = []
        try:
            for x in lines:
                x = x.strip().replace("\t", " ")
                split = x.split(" ")

                #TODO substitute magic number
                if x and len(split) == 4 and len(lines) == 4:
                    model.append([int(y) for y in split if y])
                else:
                    raise TypeError

            return Model(model)

        except TypeError:
            logging.error("Model format " + str(lines) + " is incorrect")
