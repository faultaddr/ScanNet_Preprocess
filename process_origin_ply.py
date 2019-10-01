# coding=utf -8 
'''
 author: Noesis Pan
'''
from plyfile import PlyElement,PlyData
from util import *
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor

ROOT_PATH_LABEL='/data/ScanNet_origin/scans'
ROOT_PATH='/media/scans'
PATH='/media/ScanNet_labels'
def get_point_label(path):
    label_list=[]
    ply_data=read_ply(path)
    points=ply_data.elements[0].data[0:]
    for p in points:
        label_list.append(p[6])
    return label_list

def get_point_feature(path):
    ply_data=read_ply(path)
    points=ply_data.elements[0].data[0:]
    return points

def opt(path):
    dir_name=path.split('/')[-1]
    labels=get_point_label(os.path.join(ROOT_PATH_LABEL,dir_name,dir_name+'_vh_clean_2.labels.ply'))

    points=get_point_feature(os.path.join(ROOT_PATH,dir_name,dir_name+'_vh_clean_2.ply'))
    new_points=[]
    points=[list(p)[0:6] for p in points]
    for i,p in enumerate(points):
        points[i].append(labels[i])
    points=[tuple(p) for p in points]
    vertex=np.array(points,dtype=[('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1'), ('label', '<u2')])
    el=PlyElement.describe(vertex,'vertex')
    os.makedirs(os.path.join(PATH,dir_name))
    PlyData([el]).write(os.path.join(PATH,dir_name,dir_name+'.ply'))

def main():
    if not os.path.exists(PATH):
        os.makedirs(PATH)
    dir_list=[os.path.join(ROOT_PATH_LABEL,p) for p in os.listdir(ROOT_PATH_LABEL)]
    dir_list=sorted(dir_list)
    pool =ProcessPoolExecutor(max_workers=10)
    result=list(pool.map(opt,dir_list))
    for i in result:
        print(i)

main()
