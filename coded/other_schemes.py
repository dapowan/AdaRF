'''
@author: dapowan
@file: other_schemes.py
@time: 2019-5-20 20:52
@desc: The implementations of RF-Scanner and STPP. Note that the implementations of Tagoram and MobiTagbot are in the 'hologram.py'.
'''

import numpy as np
from scipy.optimize import curve_fit

con = 4 * np.pi / 299792458.0


def rf_scanner(phases, xs, fres):
     '''
     Estimate tag position by the algorithm proposed in RF-Scanner.

     :param phases: 2-dimension ndarray. Phases collected at all aperture point under different frequency.
        The first dimension represents the index of frequency.
        The second dimension represents the index of aperture point.
     :param xs: 2-dimension ndarray. The x-coordinates of all aperture points.
        The first dimension represents the index of frequency.
        The second dimension represents the index of aperture point.
     :param fres: list. list of adopted frequency.
     
     :return: list. The estimated coordinate of tag. (X, Y)
    '''
    es = np.zeros((len(fres), 2))
    for f in range(len(fres)):
        cs = fres[f] * con
        def poly_func(x, a, b, c):
            return cs * ((x - a) ** 2 + b ** 2) ** 0.5 + c
        para, _ = curve_fit(poly_func, xs[f, :], phases[f, :])
        es[f, 0] = para[0]
        es[f, 1] = para[1]
    re = np.mean(es, 0)
    re[0] = __range_cut(re[0])
    re[1] = __range_cut(re[1])
    return re


def stpp(phases, xs, fres, aperture_spacing=0.02, ref_x=0.5, ref_y=0.5):
    '''
     Estimate tag position by the algorithm proposed in STPP.

     :param phases: 2-dimension ndarray. Phases collected at all aperture point under different frequency.
        The first dimension represents the index of frequency.
        The second dimension represents the index of aperture point.
     :param xs: 2-dimension ndarray. The x-coordinates of all aperture points.
        The first dimension represents the index of frequency.
        The second dimension represents the index of aperture point.
     :param fres: list. list of adopted frequency.
     :param aperture_spacing: float. The separation between adjacent aperture points.
     :param ref_x: reference x-coordinate.
     :param ref_y: reference y-coordinate.
     
     :return: list. The estimated coordinate of tag. (X, Y)
    '''
    stpp_phase_ref, stpp_index_ref = __stpp_init(xs, fres, aperture_spacing=aperture_spacing,
                                                      ref_x=ref_x, ref_y=ref_y)
    results = []
    for f in range(len(fres)):
        phases_f = phases[f] % (2 * np.pi)
        r = __stpp_dtw(phases_f, stpp_phase_ref[f], stpp_index_ref, xs[f])
        if r is not None:
            results.append(r)
    if len(results) > 0:
        re = np.mean(results)
        return __range_cut(re)
    else:
        return 0.0


def __stpp_dtw(phase, phase_ref, index_ref, xs):
    '''
    detect V-zone by matching measured phases with reference phases.

    :param phase:
    :param phase_ref:
    :param index_ref:
    :param xs:
    :return:
    '''
    matrix_dis = np.zeros((len(phase), len(phase_ref)))
    for i in range(len(phase)):
        for j in range(len(phase_ref)):
            matrix_dis[i, j] = np.abs(phase[i] - phase_ref[j])
    matrix_path = np.zeros((len(phase), len(phase_ref), 2), dtype=np.int)
    matrix_match = np.zeros((len(phase), len(phase_ref)))
    matrix_match[0, :] = matrix_dis[0, :]
    matrix_match[:, 0] = matrix_dis[:, 0]
    for i in range(1, len(phase)):
        for j in range(1, len(phase_ref)):
            if matrix_dis[i, j - 1] < matrix_dis[i - 1, j]:
                if matrix_dis[i, j - 1] < matrix_dis[i - 1, j - 1]:
                    matrix_match[i, j] = matrix_match[i, j - 1] + matrix_match[i, j]
                    matrix_path[i, j] = [i, j - 1]
                else:
                    matrix_match[i, j] = matrix_match[i - 1, j - 1] + matrix_match[i, j]
                    matrix_path[i, j] = [i - 1, j - 1]
            else:
                if matrix_dis[i - 1, j] < matrix_dis[i - 1, j - 1]:
                    matrix_match[i, j] = matrix_match[i - 1, j] + matrix_match[i, j]
                    matrix_path[i, j] = [i - 1, j]
                else:
                    matrix_match[i, j] = matrix_match[i - 1, j - 1] + matrix_match[i, j]
                    matrix_path[i, j] = [i - 1, j - 1]
    index = [len(phase) - 1, len(phase_ref) - 1]
    indexes = []
    while index[1] >= index_ref:
        if index[1] == index_ref:
            indexes.append(index[0])
        index = matrix_path[index[0], index[1]]

    if len(indexes) > 0:
        index_left = indexes[0]
        phase_c = phase[index_left]
        while index_left >= 0 and abs(phase[index_left] - phase_c) < np.pi:
            phase_c = phase[index_left]
            index_left = index_left - 1

        index_right = indexes[len(indexes) - 1]
        phase_c = phase[index_right]
        while index_right <= len(phase) - 1 and abs(phase[index_right] - phase_c) < np.pi:
            phase_c = phase[index_right]
            index_right = index_right + 1

        if index_left == index_right:
            return xs[index_left]
        return __stpp_curve_fiting(phase[index_left + 1:index_right], xs[index_left + 1:index_right])
    else:
        return None


def __stpp_init(xs, fres, aperture_spacing=0.02, ref_x=None, ref_y=None):
    '''
    Create reference phase profile.

    :param xs: 2-dimension ndarray. The x-coordinates of all aperture points.
        The first dimension represents the index of frequency.
        The second dimension represents the index of aperture point.
    :param fres: list. list of adopted frequency.
    :param aperture_spacing: float. The separation between adjacent aperture points.
    :param ref_x: reference x-coordinate.
    :param ref_y: reference y-coordinate.
    :return:
    stpp_phase_ref:  2-dimensional ndarray. reference phase profile.
    stpp_index_ref: int. index of reference x-coordinate in stpp_phase_ref.
    '''
    dis = pow(pow(xs - ref_x, 2) + pow(ref_y, 2), 0.5)
    phase_ref = (dis.T * fres * con).T
    phase_ref = phase_ref % (2 * np.pi)
    stpp_phase_ref = phase_ref
    stpp_index_ref = int(np.around(ref_x / aperture_spacing)) - 1
    return stpp_phase_ref, stpp_index_ref


def __stpp_curve_fiting(phases, xs):
    '''
     Estimate tag position by the curve fitting.
    '''
    po = np.polyfit(xs, phases, 2)
    return - po[1] / (2 * po[0])


def __range_cut(number, min=0.0, max=1.0):
    '''
     Handle outilers and make sure estimated tag positions are in a specific range.
    '''
    if number < min:
        return min
    elif number > max:
        return max
    else:
        return number
