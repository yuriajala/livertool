#!/usr/bin/python3
import numpy as np
import itertools
"""
This is the geometric relation descriptor module. It is responsible for computing the descriptor
for a given set of points.
"""

"""
> Function: compute
> Description: it computes the angle and the euclidian distance of pairs of
points in a set of points.
> Parameters:
* signal: the set of points (numpy array) from which
the descriptor is going to be computed.
* neigh: the number of neighbors to look forward on the algorithm. Default is 6.
> Output: the descriptor (a list of tuples [(dist12, angle12) (dist13, angle13)...]- floating values).
> Test: print (compute([0.05907967, 0.09579709, 0.06222491, 0.08984209, 0.06254953, 0.08936251, 0.06029224]))
"""
def normalize(signal):

    return signal / np.linalg.norm(signal)

def get_pairs(signal_norm, neigh=6):
    '''Retorna a combinação de n pares consecutivos a um dado ponto em uma sequência.
    Ex:
    signal_norm = [1,2,3,4]
    neigh = 2
    res = [(1,2), (1,3), (2,3), (2,4), (3,4)]
    '''

    nmax = len(signal_norm)
    if neigh >= nmax:
        neigh = nmax - 1

    left_res = []
    right_res = []

    m = 1
    for i in range(nmax - neigh):
        left_res.append(np.repeat(signal_norm[i], neigh))
        right_res.append(signal_norm[m:m + neigh])
        m = m + 1

    k = 1
    for i in range(neigh - 1):
        left_res.append(np.repeat(signal_norm[nmax - neigh + i], neigh - k))
        right_res.append(signal_norm[nmax - neigh + k:nmax + i])
        k = k + 1

    left_res = [item for sublist in left_res for item in sublist]  # flatten
    right_res = [item for sublist in right_res for item in sublist]  # flatten

    res = np.dstack((left_res, right_res))  # junta os dados
    res = res[0]  # remove array externo
    res_tuple = [tuple(l) for l in res]

    return res_tuple


def calc_dist_angle(p0, p1, idx0, idx1):
    '''
    funciona para pontos dentro do dominio x:[0,1], y:[0,1] (supondo o sinal de modulo normalizado pela norma de frobenius)
    Returns the distance and angle between two GRE IP-OP points normalized between [0,1], considering  the vertical Y axis as zero-reference
    for the angle.
    parameters: p0 , p1 -> y-value (intensity) of the points between [0,1]
    returns:    dist_norm, theta_norm - > distance and angle normalized between [0,1]
    '''
    # a diferença de altura é dada simplesmente pela subtração de p1 - p0, sendo positiva se p1 > p0 e negativa caso contrário.
    # height = p1-p0
    # height_min = -1
    # height_max = 1
    # height_norm = (height-height_min)/(height_max-height_min)

    # gera 2 pontos de TE e subtrai o primeiro do segundo (obter a base de tempo)
    # o multiplicador de 1000 lineariza a função cosseno (verificar essa explicação!)
    # time = 1000*(discrete_timeseries(2))[1]-(discrete_timeseries(2))[0]
    time = idx1 - idx0

    # como não é um triângulo retângulo, vamos usar a lei dos cossenos para obter o ângulo
    # e a distância sai junto
    # para o ângulo a referência de zero grau é a posição 12 horas, paralela ao eixo y

    # obtem lados do triângulo, valor 2 foi usado como altura total em a e b para não dar erro quando p0=1
    a = np.sqrt(np.square(2 - p1) + np.square(time))  # a corresponde ao lado superior
    b = 2 - p0  # b corresponde ao lado paralelo ao eixo y
    c = np.sqrt(np.square(p1 - p0) + np.square(time))  # c corresponde ao lado que conecta os pontos p0 e p1

    distance = c
    cosA = (np.square(b) + np.square(c) - np.square(a)) / (2 * b * c)  # lei dos cossenos
    theta_rad = np.arccos(cosA)

    # a função deve retornar a distância e ângulo normalizados entre 0 e 1. Uma função normalizada assim é dada por:
    # F(x)[0,1] = (f(x)-min(f(x)))/(max(f(x)-min(f(x)))
    # precisamos então calcular as valores de de distância e ângulo nos extremos.
    time_min = 1
    time_max = 6
    delta_p_min = 0  # distancia em altura entre p0 e p1 minimima (pts alinhados)
    delta_p_max = 1  # distancia em altura entre p0 e p1 max (pts em 0 e 1)
    # valor minimo que a distancia pode atingir
    dist_min = np.sqrt(np.square(delta_p_min) + np.square(time_min))
    # valor máximo que a distancia pode atingir
    dist_max = np.sqrt(np.square(delta_p_max) + np.square(time_max))
    # normalização
    dist_norm = (distance - dist_min) / (dist_max - dist_min)

    # para normalizar o ângulo, calcula-se o menor e maior valor do ângulo (rad)
    # o menor ocorre quando (p0,p1) = (0,1)
    p0_min = 0
    p1_min = 1
    a_min = np.sqrt(np.square(2 - p1_min) + np.square(time_min))  # a corresponde ao lado superior
    b_min = 2 - p0_min  # b corresponde ao lado paralelo ao eixo y
    c_min = np.sqrt(
        np.square(p0_min - p1_min) + np.square(time_min))  # c corresponde ao lado que conecta os pontos p0 e p1

    cosA_min = (np.square(b_min) + np.square(c_min) - np.square(a_min)) / (2 * b_min * c_min)  # lei dos cossenos
    theta_min = np.arccos(cosA_min)
    # o maior ocorre quando (p0,p1) = (1,0)
    # o cálculo do maior valor pode ser obtido subtraindo pi (equivalente a 180 graus) do resultado do menor ângulo
    theta_max = np.pi - theta_min
    # normalização
    theta_norm = (theta_rad - theta_min) / (theta_max - theta_min)

    # return height_norm, dist_norm, theta_norm
    return dist_norm, theta_norm

#
# def compute(signal, neigh=6):
#     from itertools import chain
#     signal_descriptors = []
#     signal_norm = normalize(signal)
#     signal_pairs = get_pairs(signal_norm, neigh)
#     for x in signal_pairs:
#         signal_descriptors.append(calc_dist_angle(x[0], x[1]))
#     return np.array([list(chain.from_iterable(signal_descriptors))])

def compute(signal):
    from itertools import chain
    signal_descriptors = []
    signal_norm = normalize(signal)
    signal_pairs = list(itertools.combinations(signal_norm, 2))
    signal_idx = list((i, j) for ((i, _), (j, _)) in itertools.combinations(enumerate(signal_norm), 2))
    for x, y in zip(signal_pairs, signal_idx):
        signal_descriptors.append(calc_dist_angle(x[0], x[1], y[0], y[1]))
    return np.array([list(chain.from_iterable(signal_descriptors))])