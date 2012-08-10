#!/usr/bin/python3
import os
import pre
import isan.tagging.inc_segger
import weibo_segger
import sys


N=10
fmt="./isan/utls/divde.py {0}:training.{0}.{3} {1}:test.{0}.{3} {2}:training.{0}.{3} < training.{3}"
f1s=[]
for i in range(N):
    os.system(fmt.format(i,1,4-i,'raw'))
    os.system(fmt.format(i,1,4-i,'result'))
    
    set_id=i
    print(set_id)
    model=weibo_segger.Weibo_Model("model.bin",weibo_segger.Segmentation_Space(beam_width=8))
    model.train("training.{0}.raw".format(set_id),"training.{0}.result".format(set_id),15)

    eval=model.test("test.{0}.raw".format(set_id),"test.{0}.result".format(set_id))
    f1s.append(eval.get_prf(seg=True)[2])
print(sum(f1s)/len(f1s))
