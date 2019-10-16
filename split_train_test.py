#coding = utf-8
import os
import shutil
TRAIN_PATH='./train_v9/'
VAL_PATH='./val_v9/'

def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def split_train():
    train_path = [os.path.join('./new_json_v2_other_in(copy 2)', p.strip()+'.json')
                  for p in open('./train.txt', 'r').readlines()]
    check_path(TRAIN_PATH)
    for p in train_path:
        shutil.copy(p, TRAIN_PATH+p.split('/')[-1])
    val_path = [os.path.join('./new_json_v2_other_in(copy 2)', p.strip()+'.json')
                for p in open('./val.txt', 'r').readlines()]
    check_path(VAL_PATH)
    for p in val_path:
        shutil.copy(p, VAL_PATH+p.split('/')[-1])


split_train()
