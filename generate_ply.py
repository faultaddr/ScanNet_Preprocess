# coding =utf-8

import os
import json
from plyfile import PlyData, PlyElement
import open3d as o3d
import colorsys
import random
import numpy as np

ROOT_PATH = './new_json_v1_other'


def write_ply(path, label, index):
    points = []
    for p in path:
        points.extend(get_ply_data(p, index))
    el = PlyElement.describe(np.array(points), 'vertex')
    if not os.path.exists(os.path.join('/media/ScanNet-Preprocess/new_ply_tree_other',
                                       path[0].split('/')[-2], label.split('-')[0])):
        os.makedirs(os.path.join('/media/ScanNet-Preprocess/new_ply_tree_other',
                                 path[0].split('/')[-2], label.split('-')[0]))
    PlyData([el]).write(os.path.join('/media/ScanNet-Preprocess/new_ply_tree_other', path[0].split('/')[-2],
                                     label.split('-')[0]+'/'+label+'.ply'))


def get_n_hls_colors(num):
    hls_colors = []
    i = 0
    step = 360.0 / num
    while i < 360:
        h = i
        s = 90 + random.random() * 10
        l = 50 + random.random() * 10
        _hlsc = [h / 360.0, l / 100.0, s / 100.0]
        hls_colors.append(_hlsc)
        i += step
    return hls_colors


def ncolors(num):
    rgb_colors = []
    if num < 1:
        return rgb_colors
    hls_colors = get_n_hls_colors(num)
    for hlsc in hls_colors:
        _r, _g, _b = colorsys.hls_to_rgb(hlsc[0], hlsc[1], hlsc[2])
        r, g, b = [int(x * 255.0) for x in (_r, _g, _b)]
        rgb_colors.append([r, g, b])
    return rgb_colors


color_list = ncolors(20)


def get_ply_data(path, color_index):
    with open(path, 'rb')as fp:
        ply_data = PlyData.read(fp)
        point_list = ply_data.elements[0].data[0:]
        for p in point_list:
            p[3] = color_list[color_index][0]
            p[4] = color_list[color_index][1]
            p[5] = color_list[color_index][2]
        return point_list


def read_json(path):
    areas = []
    groups = []
    group_path = []
    data = json.load(open(path))
    for i, d in enumerate(data):
        if d['label'] == '':
            areas.append(d)
        else:
            if d['parent']==-1:
                group_path.append([d['path']])

    for i, d in enumerate(areas):
        child_list = d['children']
        groups.append(child_list)
    for i, g in enumerate(groups):
        path_list = []
        for child in g:
            path_list.append(data[child]['path'])
        group_path.append(path_list)
    for i, paths in enumerate(group_path):
        for j, path in enumerate(paths):
            write_ply(path, label=str(i)+'-'+str(j), index=i)
        write_ply([i for p in paths for i in p], label=str(i), index=i)


# read_json('./train_other_v1/scene0000_00.json')
# path_list = [os.path.join(ROOT_PATH, p)for p in os.listdir(ROOT_PATH)]
# for p in path_list:
#     read_json(p)
read_json('./new_json_v1_other/scene0000_00.json')