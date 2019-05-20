'''
@author: dapowan
@file: extract_signal_profile.py
@time: 2019-5-20 14:54
@desc: extract signal profiles from CSV files.
'''

import os
import numpy as np


from coded.config import CONFIG_D1_TRAIN, CONFIG_D1_TEST


def extract_signal_profile(config, folder_experiment):
    '''
    extract phase and RSSI in one experiment

    :param config: dic. Config of a dataset.
    :param folder_experiment: str. Folder of an experiment.
    :return:
    profile: 4-dimensional ndarray. The signal profiles of give EPCs and frequencies collected at all aperture points.
        The first dimension is the index of EPC.
        The second one is the index of indicator, 0 represents phase while 1 represents RSSI.
        The third one is the index of frequency.
        The fourth one is the index of aperture point.
    xs: 2-dimensional ndarray. The x-coordinates of all aperture points.
        The first one is the index of frequency.
        The second one is the index of aperture point.
    '''
    data = read_file(config['path'] + folder_experiment)
    profile, xs = extract_profile(data, config['EPC'], config['frequency'])
    return profile, xs


def read_file(path):
    """

    :param
    path: str, directory. The path of an experiment
    :return:
    data: list. its size equals the number of aperture points.
    """
    if os.path.isdir(path):
        data = []
        #
        for index in range(len(os.listdir(path))):
            # if index % 4 == 0:
            data.append(np.loadtxt(path + '/' + str(index) + '.csv', delimiter=',', skiprows=1,
                                   dtype=[('epc', '|S24'), ('antennaIndex', '<i1'), ('frequency', '<i4'),
                                          ('time', '<i1'),
                                          ('RSSI', '<f2'), ('phase', '<f8'), ('dopplerShift', '<f2'),
                                          ('velocity', '<f2'),
                                          ('x', '<f2'), ('y', '<f2'), ('z', '<f2'), ('angle', '<f2')]))
        return data
    else:

        data = np.loadtxt(path, delimiter=',', skiprows=1,
                          dtype=[('epc', '|S24'), ('antennaIndex', '<i1'), ('frequency', '<i4'), ('time', '<i1'),
                                 ('RSSI', '<f2'), ('phase', '<f8'), ('dopplerShift', '<f2'), ('velocity', '<f2'),
                                 ('x', '<f2'), ('y', '<f2'), ('z', '<f2'), ('angle', '<f2')])
        return data



def extract_profile(data, epcs, fres):
    '''
    extract RSSI and phase from the raw signal data according to the given EPC and frequency.

    :param data: list. Output of function 'read_file'
    :param epcs: list. List of EPC.
    :param fres: list. list of frequency.
    :return:
    '''
    len_pos = len(data)
    len_fres = len(fres)
    epc_data = np.zeros((len(epcs), 2, len_fres, len_pos))
    for index_pos,idata in enumerate(data):
        for index_epc, epc in enumerate(epcs):
            for index_fres, fre in enumerate(fres):
                tdata = idata[np.where((idata[:]['epc'] == epc) & (idata[:]['frequency'] == fre))]
                tlist = merge_rssi_phase(tdata)
                if len(tlist) > 0:
                    epc_data[index_epc, 0, index_fres, index_pos] = tlist[0]
                    epc_data[index_epc, 1, index_fres, index_pos] = tlist[1]
                else:
                    epc_data[index_epc, 0, index_fres, index_pos] = -1
                    epc_data[index_epc, 1, index_fres, index_pos] = -1
    step_x = 1.0 / len_pos
    xs = np.zeros((1,len_pos))
    xs[0, :] = np.linspace(step_x, 1.0 , len_pos)
    return epc_data, xs


def merge_rssi_phase(tdata):
    '''
    merge RSSI and phase readings of one tag collectd at one aperture point.

    :param tdata: list.
    :return: list. [phase, RSSI]
    '''
    num = tdata.shape[0]
    if num == 0:
        return []
    RSSI = np.zeros(num)
    phase = np.zeros(num)
    for i, item in enumerate(tdata):
        RSSI[i] = item['RSSI']
        phase[i] = item['phase']
    return [np.around(np.mean(phase), 4), np.around(np.mean(RSSI), 4)]


if __name__ == "__main__":
    ep = '181218-01-50-8'
    profile, xs = extract_signal_profile(CONFIG_D1_TEST,ep)