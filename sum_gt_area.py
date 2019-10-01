# coding=utf-8

import os
import json

path_list=[os.path.join('./new_json_v1_other',p)for p in os.listdir('./new_json_v1_other')]

for p in path_list:
    count=0
    data=json.load(open(p))
    for d in data:
        if d['parent']==-1:
            count+=1
    if count>10:
        print(p)

