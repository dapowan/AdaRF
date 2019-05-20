'''
@author: dapowan
@file: preprocess.py
@time: 2019-5-20 17:25
@desc: preprocess phase
'''

import numpy as np


def preprocess(phases, xs, epc=b''):
    '''
    unwrap phase profiles and remove outliers.

    :param phases: 2-dimension ndarray. Phases collected at all aperture point under different frequency.
        The first one is the index of frequency.
        The second one is the index of aperture point.
    :param xs: 2-dimension ndarray. The x-coordinates of all aperture points.
        The first one is the index of frequency.
        The second one is the index of aperture point.
    :param epc: bytes, the epc of phases and xs.
    :return:
    nphases: 2-dimension ndarray. Preprocessed phases.
    nxs: 2-dimension narray. Preprocessed xs.
    '''
    len_fre = phases.shape[0]
    nnone = phases[0, :] != -1
    for i in range(1, len_fre):
        nnone = np.logical_and(nnone, phases[i, :] != -1)
    nzero = np.where(nnone)
    nxs = np.zeros((len_fre, nzero[0].size))
    nphases = np.zeros((len_fre, nzero[0].size))
    if(nzero[0].size < phases.shape[1]):
        print("miss:" + epc.decode() + " length: " + str(nzero[0].size))
    for i in range(len_fre):
        nxs[i, :]= xs[0,:][nzero]
        temp = phases[i, :][nzero]
        nphases[i, :] = np.unwrap(temp)
    return nphases, nxs