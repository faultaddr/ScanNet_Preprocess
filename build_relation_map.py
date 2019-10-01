# coding=utf-8
import json
import os
import itertools
import numpy as np
from plyfile import PlyData, PlyElement
from pyobb.obb import OBB
import sys
import util
import random
import colorsys
from concurrent.futures import ProcessPoolExecutor
JSON_PATH = './relation_map.json'
ROOT_PATH = '/data/ScanNet_v2_2'
label_dict = {}
min_distance = 0.25


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


color_list = ncolors(40)


def get_ply_data(path, color_index):
    with open(path, 'rb')as fp:
        ply_data = PlyData.read(fp)
        point_list = ply_data.elements[0].data[0:]
        for p in point_list:
            p[3] = color_list[color_index][0]
            p[4] = color_list[color_index][1]
            p[5] = color_list[color_index][2]
        return point_list


def read_json():
    global label_dict
    with open(JSON_PATH)as fp:
        label_dict = json.load(fp)
    for (key, _) in label_dict.items():
        label_dict[key].append(key)
    keys = label_dict.keys()
    all_things = list(keys)
    all_things.extend(['picture', 'window', 'otherfurniture', 'other'])
    label_dict['picture'] = all_things
    label_dict['window'] = all_things
    label_dict['otherfurniture'] = all_things
    label_dict['other'] = all_things


def read_ply(path):
    ply_data = PlyData.read(path).elements[0][0:]
    return ply_data


def same_plane(coords_4):
    x1, y1, z1 = coords_4[0][0], coords_4[0][1], coords_4[0][2]
    x2, y2, z2 = coords_4[1][0], coords_4[1][1], coords_4[1][2]
    x3, y3, z3 = coords_4[2][0], coords_4[2][1], coords_4[2][2]
    x4, y4, z4 = coords_4[3][0], coords_4[3][1], coords_4[3][2]
    a = (x2 - x1, y2 - y1,  z2 - z1)
    a = np.array(a)
    b = (x3 - x1, y3 - y1, z3 - z1)
    b = np.array(b)
    c = (x4 - x1, y4 - y1, z4 - z1)
    c = np.array(c)
    if abs(np.inner(np.multiply(a, b), c))/6 <= 0.01:
        return True
    else:
        return False


def compute_obb(coords, return_max=False):
    obb = OBB.build_from_points(coords)
    min_xyz = obb.min
    max_xyz = obb.max
    centroid = obb.centroid
    rotation = obb.rotation
    points = obb.points
    # combined_index = []
    # for i in itertools.combinations(range(7), 4):
    #     combined_index.append([i[0], i[1], i[2], i[3]])
    # combined_xyz = [[points[index[i]]
    #                  for i in range(4)] for index in combined_index]
    # count = 0
    # mean_centroid = []
    # for xyz in combined_xyz:

    #     if same_plane(xyz):
    #         mean_centroid.append(np.mean(np.array(xyz), axis=0))
    if return_max:
        return points, [min_xyz, max_xyz]
    return points


def compute_min_dis(points_1, points_2):
    min_dis = 100

    for i in itertools.product(points_1, points_2):
        distance = calculate_distance(i[0], i[1])
        if distance < min_dis:
            min_dis = distance
    central_dis = calculate_distance(np.mean(points_1, axis=0),
                                     np.mean(points_2, axis=0))
    if central_dis < min_dis:
        min_dis = central_dis
    # max_xyz_1 = np.max(np.array(points_1), axis=0)
    # min_xyz_1 = np.min(np.array(points_1), axis=0)
    # max_xyz_2 = np.max(np.array(points_2), axis=0)
    # min_xyz_2 = np.min(np.array(points_2), axis=0)
    # four_1 = [(max_xyz_1[0], max_xyz_1[1]), (min_xyz_1[0], min_xyz_1[1]),
    #           (min_xyz_1[0], max_xyz_1[1]), (max_xyz_1[0], min_xyz_1[1])]
    # four_2 = [(max_xyz_2[0], max_xyz_2[1]), (min_xyz_2[0], min_xyz_2[1]),
    #           (min_xyz_2[0], max_xyz_2[1]), (max_xyz_2[0], min_xyz_2[1])]

    # dis = util.get_distance_simple(four_1, four_2)
    dis = util.get_distance(points_1, points_2)
    if dis < min_dis:
        min_dis = dis
    return min_dis


def calculate_distance(coords_1, coords_2):
    return np.sqrt(np.sum((coords_1 - coords_2)**2))


def build_hier(path):
    def find_index(sub_list):
        for i, mean in enumerate(mean_list):
            if (str(sub_list) == str(mean)):
                return i
    read_json()

    path_list = [os.path.join(path, p)for p in os.listdir(path)]
    path_list = sorted(path_list)
    new_path_list = []
    for p in path_list:
        label = p.split('.')[0].split('/')[-1].split('_')[0]
        # 这里是为了把other 放进去
        # if label == 'other':
        #     pass
        # else:
        new_path_list.append(p)
    # path_list = new_path_list
    mean_list = []
    label_index_dict = {}
    label_list = []
    coords_list = []
    count = 0
    index_dict = {}
    gt_leaf_list = create_leaf_node(new_path_list)
    for i, p in enumerate(new_path_list):
        label = p.split('/')[-1].split('.')[0].split('_')[0]
        # 这里是为了把 other 当做一类引入分割
        if label == 'other' or label == 'floor' or label == 'wall':
            continue
        # if label=='floor' or label== 'wall':
        #     continue
        ply_data = read_ply(p)
        if label not in label_index_dict.keys():
            label_index_dict[label] = []
        # 每类 label 对应的index
        label_index_dict[label].append(count)
        index_dict[count] = i
        count += 1
        # label 对应的index
        label_list.append(label)
        coords = ply_data.tolist()
        coords = [[c[0], c[1], c[2]] for c in coords[:]]
        coords_list.append(coords)
        obb_points = compute_obb(coords)
        # mean_coords = np.mean(coords, axis=0)
        # 所有instance 的obb 的八个顶点
        mean_list.append(obb_points)
    distance_dict = {}
    # 两两结合，计算距离
    for i in itertools.combinations(mean_list, 2):
        if not (find_index(i[0]), find_index(i[1])) in distance_dict.keys():
            distance = compute_min_dis(i[0], i[1])
            distance_dict[(find_index(i[0]), find_index(i[1]))] = distance
            distance_dict[(find_index(i[1]), find_index(i[0]))] = distance
    # distance_record_dict = {}
    # for item in distance_dict.items():
    #     key, _ = item[0], item[1]
    #     label = label_list[int(key[0])]
    #     # if label == 'otherfurniture'or label == 'picture' or label == 'window':
    #     #     continue
    #     related_labels = label_dict[label]
    #     # 跟规则匹配的index
    #     related_index = np.array([label_index_dict[r] if r in label_index_dict.keys() else None for r in
    #                               related_labels]).flatten()
    #     related_index = list(filter(None, related_index))
    #     new_related_index = []
    #     for index in related_index:
    #         new_related_index.extend(index)
    #     related_index = new_related_index
    #     if key[0] not in distance_record_dict.keys():
    #         distance_list = [(int(key[0]), index, distance_dict[(key[0], str(index))]) if int(
    #             key[0]) != index else None for index in related_index]
    #         distance_list = list(filter(None, distance_list))
    #         distance_record_dict[key[0]] = distance_list

    # group = {}
    # grouped_instance_record = []
    # for i, item in enumerate(distance_record_dict.items()):
    #     group_item = []
    #     for j in item[1]:
    #         s = j[0]
    #         t = j[1]
    #         if j[2] < 0.25:
    #             group_item.append(t)
    #     if item[1]:
    #         group[s] = group_item
    group = []
    recorded_group = []
    for i, (key, value) in enumerate(label_index_dict.items()):
        single_group = {}
        for v in itertools.product(value, value):
            if v[0] not in single_group.keys():
                single_group[v[0]] = []
            single_group[v[0]].append(v[1])
        g_list = []
        for j, (k, v)in enumerate(single_group.items()):
            g = [k]
            for m in v:
                if m != k:
                    if distance_dict[(k, m)] < 0.25:
                        g.append(m)
            g_list.append(g)
        g_list = sorted(g_list, reverse=True,
                        key=lambda parameter_list: len(parameter_list))
        # for g in g_list:
        #     g_ = []
        #     for i in g:
        #         if i not in recorded_group:
        #             g_.append((key, i))
        #             recorded_group.append(i)
        #     if g_:
        #         group.append(g_)
        g_list = find_max(k, g_list)
        new_g_list = []
        for g in g_list:
            g_ = []
            for i in g:
                g_.append((key, i))
            new_g_list.append(g_)
        group.extend(new_g_list)
    real_group = group
    # group_list = []
    # for item in group.items():
    #     key, value = item
    #     group_single_list = []
    #     group_single_list.append(key)
    #     for v in value:
    #         if label_list[key] == label_list[v]:
    #             group_single_list.append(v)
    #     group_list.append(group_single_list)

    #     # label_ = [label_list[v] for v in value]
    #     # print(label_list[key], label_)
    # group_index_record = []
    # group_list = sorted(group_list, key=lambda i: len(i), reverse=True)
    # real_group = []
    # for g in group_list:
    #     real = []
    #     for _g in g:
    #         grouped_instance_record.append(_g)
    #         if _g not in group_index_record:
    #             group_index_record.append(_g)
    #             # print(label_list[_g], _g, end=' ')
    #             real.append((label_list[_g], _g))
    #         else:
    #             continue
    #     if real:
    #         real_group.append(real)

    gt_group_list, gt_leaf_list = create_group_node(
        real_group, gt_leaf_list, index_dict)
    # TODO 计算group之间的距离。
    group_coords_list = []
    group_point_list = []
    group_label_index = {}
    for i, g in enumerate(real_group):
        single_coords = []
        for index in g:
            single_coords.extend(coords_list[index[1]])
        if g[0][0] not in group_label_index.keys():
            group_label_index[g[0][0]] = [i]
            group_coords_list.append(single_coords)
        else:
            group_label_index[g[0][0]].append(i)
            group_coords_list.append(single_coords)

    for coords in group_coords_list:
        points = compute_obb(coords)
        group_point_list.append(points)
    group_distance_dict = {}

    def find_group_index(points):
        for i, g in enumerate(group_point_list):
            if str(g) == str(points):
                return i
    for i in itertools.combinations(group_point_list, 2):
        index_0 = find_group_index(i[0])
        index_1 = find_group_index(i[1])
        if (index_0, index_1) not in group_distance_dict.keys():

            distance = compute_min_dis(i[0], i[1])

            group_distance_dict[(index_0, index_1)] = distance
            group_distance_dict[(index_1, index_0)] = distance
    related_group_index = {}
    for i, group in enumerate(real_group):
        label = group[0][0]
        # 获取规则
        related_label = label_dict[label]
        related_group_index[i] = []
        for r_label in related_label:
            if r_label in group_label_index.keys():
                related_group_index[i].extend(
                    group_label_index[r_label])
    group_distance_record = {}
    for i, (key, value)in enumerate(related_group_index.items()):
        distance_list = [(key, index, group_distance_dict[(key, index)])
                         if key != index else None for index in value]
        distance_list = list(filter(None, distance_list))
        group_distance_record[key] = distance_list
    area = []
    areaed_group_record = []
    for i, (key, value)in enumerate(group_distance_record.items()):
        area_item = []
        area_item.append(key)
        for v in value:
            if v[2] < min_distance:
                area_item.append(v[1])
        areaed_group_record.append(area_item)

    def get_lens(record):
        count = 0
        for i in record:
            count += len(real_group[i])
        return count
    areaed_group_record = sorted(
        areaed_group_record, key=lambda i: get_lens(i), reverse=True)
    areaed_record_index = []

    real_area =find_max('', areaed_group_record))
    # sys.exit()
    #### original func
    # def get_rest(record):
    #     count = 0
    #     for i in record:
    #         if i not in areaed_record_index:
    #             count += 1

    #     return count
    # while len(areaed_record_index) != len(group_point_list):
    #     areaed_group_record = sorted(
    #         areaed_group_record, key=lambda i: get_rest(i), reverse=True)
    #     new_area = []
    #     for group in areaed_group_record[0]:
    #         if group not in areaed_record_index:
    #             new_area.append(group)
    #             areaed_record_index.append(group)
    #     real_area.append(new_area)
    #     areaed_group_record.pop(0)
    # print(real_area)
    # sys.exit()
    gt_area_list, gt_group_list = create_area_node(real_area, gt_group_list)
    gt_leaf_list.extend(gt_group_list)
    gt_leaf_list.extend(gt_area_list)
    if not os.path.exists('/media/ScanNet-Preprocess/new_json_v1_other_in'):
        os.makedirs('/media/ScanNet-Preprocess/new_json_v1_other_in')
    with open('/media/ScanNet-Preprocess/new_json_v1_other_in/'+path.split('/')[-1]+'.json', 'w')as json_data:
        json.dump(gt_leaf_list, json_data, default=obj_2_json)
    #############-------------ply preview-----------##################
    # area_ply_list = []
    # for area in real_area:
    #     ply_list = []
    #     for group in area:
    #         for p in real_group[group]:
    #             ply_path = path_list[index_dict[p[1]]]
    #             ply_list.append(ply_path)
    #     area_ply_list.append(ply_list)

    # for i, area in enumerate(area_ply_list):
    #     points = []
    #     for ply in area:
    #         points.extend(get_ply_data(ply, i))
    #     el = PlyElement.describe(np.array(points), 'vertex')
        # if not os.path.exists(os.path.join('/media/ScanNet-Preprocess/new_ply', path.split('/')[-1])):
        #     os.makedirs(os.path.join(
        #         '/media/ScanNet-Preprocess/new_ply', path.split('/')[-1]))
        # PlyData([el]).write(os.path.join(
        #     '/media/ScanNet-Preprocess/new_ply', path.split('/')[-1], str(i)+'.ply'))
    '''
    gt_count=0
    for p in path_list:
        label = p.split('/')[-1].split('.')[0].split('_')[0]
        print(label)
        if label == 'other' or label == 'floor' or label == 'wall':
            gt_count+=1
    print('gt_count',gt_count)
    '''
    return path


def find_max(k, group_list):

    lens = len(list(set([i for g in group_list for i in g])))

    def in_sum(group, record):
        count = 0
        for g in group:
            if g in record:
                count += 1
        return count

    def find_left(group, record):
        return list(set(group).difference(set(record)))
    record = []
    count = 0
    groups = []
    while len(record) != lens:
        group_score = []
        for i, group in enumerate(group_list):
            score = len(group)-in_sum(group, record)
            group_score.append((i, score))
        group_score = sorted(group_score, reverse=True, key=lambda i: i[1])
        candidate_group_index = group_score[0][0]
        left = find_left(group_list[candidate_group_index], record)
        if left:
            groups.append(left)
            record.extend(left)
    return groups


class GT:
    id = 0
    parent = -1
    children = []
    label = ''
    path = ''

    def __init__(self, id=None, parent=None, children=None, label=None, path=None):
        self.id = id
        self.parent = parent
        self.children = children
        self.label = label
        self.path = path


def obj_2_json(pc):
    return {
        "id": pc.id,
        "parent": pc.parent,
        "children": pc.children,
        "label": pc.label,
        "path": pc.path
    }


def create_leaf_node(path_list):
    gt_leaf_list = []
    wall_list = []
    floor_list = []
    for i, path in enumerate(path_list):
        # if 'wall' in path:
        #     wall_list.append(path)
        # elif 'floor' in path:
        #     floor_list.append(path)
        # else:
        gt = GT()
        gt.id = i
        gt.parent = -1
        gt.children = []
        gt.label = path.split('/')[-1].split('.')[0].split('_')[0]
        gt.path = [path]
        gt_leaf_list.append(gt)

    return gt_leaf_list


def create_group_node(group_list, leaf_list, index_dict):
    gt_group_list = []
    for i, group in enumerate(group_list):
        group = [g[1] for g in group]
        gt = GT()
        gt.id = len(leaf_list)+i
        gt.parent = -1
        gt.children = [index_dict[g] for g in group]
        gt.path = []
        for g in group:
            leaf_list[index_dict[g]].parent = gt.id
            gt.path.extend(leaf_list[index_dict[g]].path)
            if gt.label == None:
                gt.label = leaf_list[index_dict[g]].label+' group'
        gt_group_list.append(gt)
    return gt_group_list, leaf_list


def create_area_node(area_list, group_list):
    gt_area_list = []
    for i, area in enumerate(area_list):
        gt = GT()
        gt.id = group_list[-1].id+i+1
        gt.parent = -1
        # gt.children =[group_list[g].id for g in group for group in area]
        gt.children = []
        gt.path = []
        gt.label = ''
        for group in area:
            gt.path.extend(group_list[group].path)
            gt.children.append(group_list[group].id)
            group_list[group].parent = gt.id
        gt_area_list.append(gt)
    return gt_area_list, group_list


#path_list = [os.path.join(ROOT_PATH, p)for p in os.listdir(ROOT_PATH)]
# for i, p in enumerate(path_list):
#     pool = ProcessPoolExecutor(max_workers=16)
#     result = list(pool.map(build_hier, p))
#     for i in result:
#         print(i)

#     build_hier(p)
#     print(i+1, '/1513', '---okay!')
build_hier(os.path.join(ROOT_PATH, 'scene0265_00'))
# pool = ProcessPoolExecutor(max_workers=10)
# result = list(pool.map(build_hier, path_list))
# for i in result:
#     pass

''' deel with error
lines=open('./error.txt').readlines()
error_list = lines

for error in error_list:
    min_distance = 0.30
    error=error.split('/')[-1].split('.')[0]
    error=os.path.join(ROOT_PATH,error)
    print(error)
    _, lens = build_hier(error)
    print(lens)
    while lens > 10:
        min_distance += 0.05
        _, lens = build_hier(error)
        print(lens)
'''
