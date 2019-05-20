'''
@author: dapowan
@file: reconstruct_tag_location.py
@time: 2019-5-20 17:16
@desc: read config and reconstruct tag location.
'''

import numpy as np

def read_config(path, year='19'):
    dict = {}
    with open(path) as file:
        data = file.readlines()
        for i, line in enumerate(data):
            if i > 0:
                items = line.split(' ')
                folder_date = year + items[0]
                mix_items = items[1].split(':')
                order_items = mix_items[0].split('-')
                order_start = int(order_items[0])
                order_end = int(order_items[1])
                x_center = float(mix_items[1])
                y = float(items[2])
                for j in range(order_start, order_end + 1):
                    folder = folder_date + '-' + '{0:02d}'.format(j) + '-' + items[3] + '-' + items[4].replace('\n', '')
                    dict[folder] = [x_center, y]
    return dict


def create_truth(x_center, y, num, gap=20, lines=None, line_spacing=None, extra=0.0):
    truth = []
    if lines is None:
        index = np.mean(np.arange(num))
        for i in range(num):
            if i > index:
                truth.append([(x_center + gap * (i - index) + extra) / 100.0, y / 100.0])
            elif i < index:
                truth.append([(x_center + gap * (i - index) - extra) / 100.0, y / 100.0])
            else:
                truth.append([(x_center + gap * (i - index)) / 100.0, y / 100.0])
    else:
        for l, line in enumerate(lines):
            dis_y = (y ** 2 + line_spacing[l] ** 2) ** 0.5
            index = np.mean(np.arange(line))
            for i in range(line):
                if i < index:
                    truth.append([(x_center + gap * (i - index) + extra) / 100.0, dis_y / 100.0])
                elif i > index:
                    truth.append([(x_center + gap * (i - index) - extra) / 100.0, dis_y / 100.0])
                else:
                    truth.append([(x_center + gap * (i - index)) / 100.0, dis_y / 100.0])
    return truth
