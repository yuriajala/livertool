from modules.ml import load_model;
from modules.ml import geo_rel_descriptor;

def initialize():
    FFTYPE = "100FF"
    ATTRIBUTE_NB = 42
    #ATTRIBUTE_NB = 21
    OPTIMIZER = "adam"  # rprop or sgd - for a while
    HIDDEN_NETWORK_LAYERS_LATTICE = [32, 16, 2]
    ACTIVATION_TYPE = "relu"  # relu, tanh, sigmoid, softplus, softsign
    model, model_path = load_model.load(FFTYPE, ATTRIBUTE_NB, OPTIMIZER, ACTIVATION_TYPE, HIDDEN_NETWORK_LAYERS_LATTICE)
    return model, model_path

def compute(signal, model, model_path, *args):
    descriptor = geo_rel_descriptor.compute(signal)
    return model.predict(descriptor)
