#coding = utf-8
import os
import shutil


def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def split_train():
    train_path = [os.path.join('./scannet_json', p.strip()+'.json')
                  for p in open('./train.txt', 'r').readlines()]
    check_path('./train_v2')
    for p in train_path:
        shutil.copy(p, './train_v2/'+p.split('/')[-1])
    val_path = [os.path.join('./scannet_json', p.strip()+'.json')
                for p in open('./val.txt', 'r').readlines()]
    check_path('./val_v2')
    for p in val_path:
        shutil.copy(p, './val_v2/'+p.split('/')[-1])


split_train()
