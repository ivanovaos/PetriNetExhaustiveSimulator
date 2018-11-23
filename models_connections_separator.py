__author__ = "Olga Ivanova"
__date__ = "31.08.2016"
__version__ = "1.0"
__maintainer__ = "Olga Ivanova"
__email__ = "ivanovaos.09@gmail.com"
__status__ = "Production"
__organization__ = "Vrije Universiteit Amsterdam"

import sys, getopt
import os
from os.path import basename, splitext

from model.model_handler import ModelHandler


def read_args(args):
    inputfile = ""
    outputpath = ""

    try:
      opts, args = getopt.getopt(args, "hi:p:", ["ifile=", "ppath="])
    except getopt.GetoptError:
      print('model_filter.py -i <inputfile> -p <outputpath>')
      sys.exit(2)

    for opt, arg in opts:
      if opt == '-h':
         print('models_connections_separator.py -i <inputfile> -p <outputpath>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-p", "--opath"):
         outputpath = arg

    return{"inputfile": inputfile, "outputpath": outputpath}


if __name__ == '__main__':
    args = sys.argv[1:]
    assigned_args = read_args(args)
    input_file = assigned_args["inputfile"]
    input_file_name = splitext(basename(input_file))[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    ModelHandler.set_path(dir_path)

    models = ModelHandler.read_models_in_line(input_file)

    inversions_file = open(dir_path + assigned_args["inputfile"], "r")

    if not os.path.exists(dir_path + assigned_args["outputpath"]):
            os.makedirs(dir_path + assigned_args["outputpath"])

    files = {}
    n = 0
    for line in inversions_file:
        model = ModelHandler.read_one_model_line(line)
        n_conn = model.get_connection_num()
        if n_conn not in files.keys():
            files[n_conn] = open(dir_path + assigned_args["outputpath"] + "/" +
                        input_file_name + "_" + str(n_conn) + ".txt", "w")

        files[n_conn].write(line)

        print(line + str(n))
        n += 1


    for file in files.values():
        file.close()
