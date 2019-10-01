# coding =utf-8
import os
import json
from util import *


def adjust(path):
    data = read_json(path)
    new_data = []
    for d in data:
        if 'group' in d['label'] and len(d['path']) == 1:
            child = d['children'][0]
            new_data[child]['parent'] = d['parent']
            data[d['parent']]['children'].remove(d['id'])
            data[d['parent']]['children'].append(new_data[child]['id'])
        elif d['label'] == '' and len(d['path']) == 1:
            new_d = d
            new_d['label'] = d['path'][0].split(
                '/')[-1].split('.')[0].split('_')[0]
            new_d['children'] = []
            new_data.append(new_d)
        else:
            new_data.append(d)
    print(new_data)
    write_json(path, new_data)


adjust('/media/ScanNet-Preprocess/train_other_v1/scene0000_01.json')
