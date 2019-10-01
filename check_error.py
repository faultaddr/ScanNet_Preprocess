# coding=utf-8
import json

import os


def opt_area_json(path):
    json_data = json.load(open(path, 'r'))
    new_json_data = []
    for data in json_data:
        if data['label'] == '':
            new_data = data
            new_data['id'] = data['id']+1
            new_json_data.append(new_data)

        else:
            new_data = data
            if ' group' in data['label']:
                new_data['parent'] = data['parent']+1
            new_json_data.append(new_data)
    with open(path, 'w')as fp:
        json.dump(new_json_data, fp)


def opt_other_json(path):
    json_data = json.load(open(path, 'r'))
    new_json_data = []
    flag = False
    index = 0
    for i, data in enumerate(json_data):
        if data['label'] == 'other':
            index = i
            flag = True
    if flag:
        for i, data in enumerate(json_data):
            node = data
            if data['label'] != 'other':
                if data['id'] > index:
                    node['id'] = data['id']-1

                new_child = []
                for child in data['children']:
                    if child > index:
                        new_child.append(child-1)
                    else:
                        new_child.append(child)
                if node['parent'] > index:
                    node['parent'] = node['parent']-1
                node['children'] = new_child
                new_json_data.append(node)
    with open(path, 'w')as fp:
        json.dump(new_json_data, fp)


path_list = [os.path.join('./train(copy)', p)
             for p in os.listdir('./train(copy)')]
for p in path_list:
    opt_area_json(p)
