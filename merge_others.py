# coding =utf-8

import os

import json
import sys
import copy
from util import *


def merge(path):
    def get_other_path(other):
        path = other['path']
        return path

    def remove_none(obj):
        if obj is not None:
            return True
        else:
            return False

    data = read_json(path)
    new_data = copy.deepcopy(data)
    for i, d in enumerate(data):
        other_list = []
        other_id_list = []
        if 'group' in d['label']:
            for child in d['children']:
                if data[child]['label'] == 'other':
                    other_list.append(data[child])
        for other in other_list:
            new_data[other['id']]['parent'] = d['id']
            other_id_list.append(other['id'])
        if len(other_list) > 1:
            gt = GT()
            gt.id = len(new_data)
            gt.children = [other['id'] for other in other_list]
            gt.label = 'other group'
            gt.path = [other['path'][0] for other in other_list]
            gt.parent = d['id']
            new_data.append(obj_2_json(gt))
            origin_child_list = d['children']
            print(origin_child_list)
            merged_child_list = [child if child not in other_id_list else None for child in origin_child_list]
            print(merged_child_list)
            merged_child_list = list(filter(remove_none, merged_child_list))
            print(merged_child_list)
            if not merged_child_list:
                print(path, d['label'])
            merged_child_list.extend([gt.id])
            new_data[i]['children'] = merged_child_list
    with open(path, 'w')as fp:
        json.dump(new_data, fp)


if __name__ == '__main__':
    path_list = [p for p in os.listdir('new_json_v2_other_in(copy)_1')]
    for p in path_list:
        try:
            merge('new_json_v2_other_in(copy)_1/' + p)
        except Exception:
            print(p)
