# coding=utf-8
import json

import os
from util import read_json
import copy
import sys


def opt_area_json(path):
    json_data = json.load(open(path, 'r'))
    new_json_data = []
    for data in json_data:
        if data['label'] == '':
            new_data = data
            new_data['id'] = data['id'] + 1
            new_json_data.append(new_data)

        else:
            new_data = data
            if ' group' in data['label']:
                new_data['parent'] = data['parent'] + 1
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
                    node['id'] = data['id'] - 1

                new_child = []
                for child in data['children']:
                    if child > index:
                        new_child.append(child - 1)
                    else:
                        new_child.append(child)
                if node['parent'] > index:
                    node['parent'] = node['parent'] - 1
                node['children'] = new_child
                new_json_data.append(node)
    with open(path, 'w')as fp:
        json.dump(new_json_data, fp)


def add_other_2_area(path):
    data = read_json(path)
    for i, d in enumerate(data):
        if d['label'] == '':
            data[i]['path'] = []
            for child in d['children']:
                data[i]['path'].extend(data[child]['path'])
    json.dump(data, open(path, 'w'))


def check_single_child(path):
    flag = False
    data = read_json(path)
    for d in data:
        if len(d['path']) == 1 and d['parent'] == -1 and d['label'] == '':
            flag = True
    if flag:
        return path


def change_id(path):
    data = read_json(path)
    id_map = {}
    for i, d in enumerate(data):
        id_map[d['id']] = i
    print(id_map)
    for i, d in enumerate(data):
        if d['parent'] != -1:
            data[i]['parent'] = id_map[d['parent']]
        if d['children'] != []:
            for j, child in enumerate(d['children']):
                data[i]['children'][j] = id_map[d['children'][j]]
        data[i]['id'] = id_map[d['id']]
    json.dump(data, open(path, 'w'))


def add_other(path_list):
    for p in path_list:
        add_other_2_area(p)


def reduce_hier(error_list):
    def not_empty(j):
        if j == {}:
            return False
        else:
            return True

    for p in error_list:
        data = read_json(p)
        new_data = []
        for i, d in enumerate(data):
            if len(d['path']) == 1 and d['parent'] == -1 and d['label'] == '':
                data[data[d['children'][0]]['children'][0]]['parent'] = -1
                data[d['children'][0]] = {}
                data[i] = {}
        for d in data:
            if not str(d) == '{}':
                new_data.append(d)

        json.dump(new_data, open(p, 'w'))


def reduce_group(err_list):
    for err in err_list:
        print(err)
        data = read_json(err)
        new_data = copy.deepcopy(data)
        for i, d in enumerate(data):
            if 'group' in d['label'] and len(d['children']) == 1:
                parent = d['parent']
                child = d['children'][0]
                id = d['id']
                assert len(d['children']) == 1
                print(parent, id, d['label'])
                print(data[parent])
                index = data[parent]['children'].index(id)
                new_data[parent]['children'][index] = child
                new_data[child]['parent'] = parent
                new_data[i] = {}
        print(new_data)
        print(list(filter(lambda i: False if i == {} else True, new_data)))
        new_data = list(filter(lambda i: False if i == {} else True, new_data))
        with open(err, 'w')as fp:
            json.dump(new_data, fp)


def reduce_other_group(path_list):
    for p in path_list:
        data = read_json(p)
        for i, d in enumerate(data):
            if d['label'] == 'other group':
                data[i]['children'] = []
        with open(p, 'w')as fp:
            json.dump(data, fp)


def reduce_area(path_list):
    for p in path_list:
        data = read_json(p)
        for i, d in enumerate(data):
            if d['parent'] == -1 and len(d['children']) == 1 and d['label'] == '':
                data[d['children'][0]]['parent'] = -1
                data[i] = {}
        new_data = list(filter(lambda i: False if i == {} else True, data))
        with open(p, 'w')as fp:
            json.dump(new_data, fp)


def delete_none(path_list):
    for p in path_list:
        new_data = []
        data = read_json(p)
        id_map = {}
        for i, d in enumerate(data):
            if str(d) != "{}":
                new_data.append(d)
        for i, d in enumerate(new_data):
            id_map[d['id']] = i
        for i, d in enumerate(new_data):
            if d['parent'] != -1:
                new_data[i]['parent'] = id_map[d['parent']]
            if d['children']:
                for j, child in enumerate(d['children']):
                    new_data[i]['children'][j] = id_map[d['children'][j]]
            new_data[i]['id'] = id_map[d['id']]
        print(new_data)
        with open(p, 'w')as fp:
            json.dump(new_data, fp)


def change_all_id(path_list):
    for p in path_list:
        print(p)
        change_id(p)

def delete_instance_level(path_list):
    for p in path_list:
        data=read_json(p)
        for i,d in enumerate(data):
            if 'group' in d['label']:
                data[i]['children']=[]
                data[i]['label']=d['label'].split()[0]
        with open(p,'w')as fp:
            json.dump(data,fp)
def add_shower_curtain(path_list):
    for p in path_list:
        data=read_json(p)
        for i,d in enumerate(data):
            if 'shower' in d['label']:
                data[i]['label']='shower curtain'
        with open(p,'w')as fp:
            json.dump(data,fp)

def main():
    path_list = [os.path.join('./new_json_v2_other_in(copy 2)', p)
                 for p in os.listdir('./new_json_v2_other_in(copy 2)')]
    # error_list = []
    # for p in path_list:
    #     result = check_single_child(p)
    #
    #     if result is not None:
    #         error_list.append(result)
    # print(len(error_list))
    # add_other(path_list=path_list)
    # reduce_hier(error_list=error_list)
    # for p in path_list:
    #     print(p)
    #     change_id(p)
    # reduce_group(path_list)
    # delete_none(path_list)
    # reduce_other_group(path_list)
    # reduce_area(path_list)
    #change_all_id(path_list)
    #delete_instance_level(path_list)
    add_shower_curtain(path_list)


main()
