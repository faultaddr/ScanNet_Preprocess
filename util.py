# coding =utf-8
from shapely.ops import nearest_points
from shapely.geometry import Polygon, LineString, MultiPoint
import numpy as np
import json
from plyfile import PlyData, PlyElement


def get_distance(points_1, points_2):
    points_1 = np.array(points_1)[:, :2]
    points_2 = np.array(points_2)[:, :2]
    new_points_1 = []
    new_points_2 = []
    for i, p in enumerate(points_1):
        new_points_1.append((p[0], p[1]))
    for i, p in enumerate(points_2):
        new_points_2.append((p[0], p[1]))
    p_1 = MultiPoint(new_points_1).convex_hull
    p_2 = MultiPoint(new_points_2).convex_hull
    # print(p_1,p_2)
    return LineString([o for o in nearest_points(p_1, p_2)]).length


def get_distance_simple(points_1, points_2):
    p_1 = MultiPoint(points_1).convex_hull
    p_2 = MultiPoint(points_2).convex_hull
    return LineString([o for o in nearest_points(p_1, p_2)]).length


def read_json(path):
    data = json.load(open(path))
    return data


def write_json(path, data):
    with open(path, 'w')as fp:
        json.dump(data, fp)


def read_ply(path):
    ply_data = PlyData.read(path)
    return ply_data


def remove_none(obj):
    if obj is not None:
        return True
    else:
        return False


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
