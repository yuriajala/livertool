# # MODEL METHODS
# ##################
import numpy

from keras.models import Sequential
from keras.layers import Dense
from keras import optimizers
import os.path
from keras.models import model_from_json

# > Model loading/creation

def load(fftype, attr_nb, optimizer, activation_type, hidden_network_layers_lattice):
    numpy.random.seed(7); # > Hardcoded seed value for reproducibility purposes

    model_name = fftype + "-model-" + str(attr_nb) + "in-" + optimizer + "-" + activation_type
    model_lattice = str(attr_nb)
    for N in hidden_network_layers_lattice:
        model_name = model_name + '-' + str(N)
        model_lattice = model_lattice + '-' + str(N)
    model_lattice = model_lattice + "-1/"
    model_path = os.path.abspath(os.path.join(__file__, '../Models/', model_lattice+model_name))
    print("> Model at: " + model_path)
    # > Load previous trained model
    if ((os.path.exists(model_path + ".json")) and
        (os.path.exists(model_path +".h5"))):

        # load json and create model
        json_file = open(model_path+".json", "r")
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        # load weights into new model
        model.load_weights(model_path+".h5")
        print("> Loaded " + model_path + " model from the disk.")
    # > Creates model from scratch
    else:
        model = None
        print("> Model not found.")
    return model, model_path

