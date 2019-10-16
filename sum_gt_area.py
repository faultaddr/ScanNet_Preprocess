# coding=utf-8

import os
import json

ROOT_PATH = './new_json_v2_other_in(copy 2)'

path_list = [os.path.join(ROOT_PATH, p) for p in os.listdir(ROOT_PATH)]
record = 0
record_error = 0
children_err_list = []
top_layer_err_list = []
count_dict = {}
for p in path_list:
    count = 0
    count_1 = 0
    try:
        data = json.load(open(p))
        for d in data:
            if d['parent'] == -1:
                count += 1
            if len(d['children']) > 10 and d['label'] != 'other group':
                count_1 = 1
        if count not in count_dict.keys():
            count_dict[count] = 1
        else:
            count_dict[count] += 1
        if count > 10:
            record += 1
            top_layer_err_list.append(p)
        if count_1 == 1:
            record_error += 1
            children_err_list.append(p)
    except Exception as e:
        record_error += 1
for p in top_layer_err_list:
    print(p)
print('---------')
for p in children_err_list:
    print(p)
print(len(top_layer_err_list), len(children_err_list))
print(count_dict)
