import os
import shutil

path_list=[p for p in os.listdir('./val_v2')]
dir_list=[]
for p in path_list:
    dir_name=p.split('.')[0]
    dir_list.append(dir_name)

for dir in dir_list:
    shutil.copy('/media/scans/'+dir+'/'+dir+'_vh_clean_2.ply','./v/'+dir+'.ply')


