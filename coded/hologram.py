'''
@author: dapowan
@file: hologram.py
@time: 2018-10-3 16:27
@desc:
'''
import time

import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


class Hologram:

    def __init__(self, paras, phases, xs, fres):
         '''
        init hologram according to the given setup.

        :param paras: list with the size of 4. Set the surveillance plane of the hologram.
            The first element defines the number of the grids along the x-axis.
            The second element defines the length of the grid along the x-axis.
            The first element defines the number of the grids along the y-axis.
            The first element defines the length of the grid along the y-axis.
        :param phases: 2-dimension ndarray. Phases collected at all aperture point under different frequency.
            The first dimension represents the index of frequency.
            The second dimension represents the index of aperture point.
        :param xs: 2-dimension ndarray. The x-coordinates of all aperture points.
            The first dimension represents the index of frequency.
            The second dimension represents the index of aperture point.
        :return: ndarray.
        '''
    
        self.num_x = paras[0]
        self.num_y = paras[1]
        self.step_x = paras[2]
        self.step_y = paras[3]
        self.phases = phases
        self.xs = xs
        self.fres = fres
        self.con = 4 * np.pi / 299792458.0
        self.stpp_phase_ref = None


    def holo_l1(self, gap = 1):
        map = np.zeros((self.num_x, self.num_y))
        [rows, cols] = map.shape
        len_pos = self.xs.shape[1]
        for r in range(rows):
            for c in range(cols):
                likelihood = 0.0
                dis = self.__distances(r, c)
                p_th = (dis.T * self.fres * self.con).T
                for g in range(len_pos):
                    if g + gap < len_pos:
                        pd_th = p_th[:, g + gap] - p_th[:, g]
                        pd_ac = self.phases[:, g + gap] - self.phases[:, g]
                        pd = pd_th - pd_ac
                        exp_pd = np.exp(pd * 1j)
                        likelihood += np.sum(exp_pd)
                likelihood = likelihood.real
                map[self.num_x - 1 - c, r] = likelihood
        map = np.exp(map - len(self.fres) * (len_pos - gap))
        map /= np.max(map)
        return map



    def holo_l2(self, gap = 1):
        map = np.zeros((self.num_x, self.num_y))
        len_pos = self.xs.shape[1]
        for r in range(self.num_x):
            for c in range(self.num_y):
                likelihood = 0.0
                dis = self.__distances(r, c)
                p_th = (dis.T * self.fres * self.con).T
                for g in range(len_pos):
                    if g + gap < len_pos:
                        pd_th = p_th[:, g + gap] - p_th[:, g]
                        pd_ac = self.phases[:, g + gap] - self.phases[:, g]
                        pd = abs(pd_th - pd_ac)
                        likelihood += np.sum(pd)
                map[self.num_x - 1 - c, r] = np.exp(-likelihood)
        map /= np.max(map)
        return map

    def holo_tagoram(self):
        nphases = self.phases.copy()
        for i in range(len(self.fres)):
            nphases[i, :] = self.phases[i, :] - self.phases[i, 0]
        nphases = np.delete(nphases, 0, 1)
        map = np.zeros((self.num_x, self.num_y))
        [rows, cols] = map.shape
        for r in range(rows):
            for c in range(cols):
                likelihood = 0.0
                dis = self.__distances(r, c)
                dis = (dis.T - (dis[:, 0]).T).T
                dis = np.delete(dis, 0, 1)
                pd_th = (dis.T * self.fres * self.con).T
                pd = pd_th - nphases
                exp_pd = np.exp(pd * 1j)
                pos_pd = (1 - stats.norm.cdf(abs(pd), 0, 0.1 * pow(2, 0.5))) * 2
                likelihood += np.sum(exp_pd * pos_pd)

                map[self.num_x - 1 - c, r] = abs(likelihood)
        map /= np.max(map)
        return map



    def holo_mobitagbot(self):
        map = np.zeros((self.num_x, self.num_y))
        [rows, cols] = map.shape
        wk = np.ones(self.xs.shape[1])
        if len(self.fres) > 2:
            phases = self.phases.copy()
            for i in range(self.xs.shape[1]):
                phases[:, i] = np.unwrap(phases[:, i])
            pd = np.zeros((phases.shape[0] - 1, phases.shape[1]))
            for f in range(len(self.fres) - 1):
                pd[f] = abs(phases[f + 1] - phases[f])
            pd_sum = np.sum(pd, 0)
            pd /= pd_sum
            pd[pd == 0.0] = 0.000001
            ek = np.sum(pd * np.log(pd), 0)
            ek /=  - np.log(phases.shape[0] - 1)
            wk = (ek / (self.xs.shape[1] - np.sum(ek)))
        for r in range(rows):
            for c in range(cols):
                likelihood = 0.0
                dis = self.__distances(r, c)
                p_th = (dis.T * self.fres * self.con).T
                pd = p_th - self.phases
                exp_pd = np.exp(pd * 1j) * wk
                likelihood += np.sum(exp_pd)
                map[self.num_x - 1 - c, r] = abs(likelihood)
        map /= np.max(map)
        return map


    def __distances(self, index_x, index_y):
        '''
        create the distances from one possible tag position to all aperture points.

        :param index_x: int.
        :param index_y: int.
        :return: ndarray.
        '''
        temp = pow(self.xs - (index_x + 1)* self.step_x, 2) + pow((index_y + 1) * self.step_y, 2)
        dis = pow(temp, 0.5)
        return dis




