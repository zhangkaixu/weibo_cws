#!/usr/bin/python3
import pre
import isan.tagging.inc_segger
import weibo_segger
import sys


"""
CWS model for weibo

input: weibo
output: segmented weibo

using a rule based preprosess and an incremental CWS model
"""


if __name__ == '__main__':
    if len(sys.argv)==1:
        set_id='1'
    else:
        set_id=sys.argv[1]
    model=weibo_segger.Weibo_Model("model.bin",weibo_segger.Segmentation_Space(beam_width=8))
    model.train("training.{0}.raw".format(set_id),"training.{0}.result".format(set_id),10)
    model.test("test.{0}.raw".format(set_id),"test.{0}.result".format(set_id))



    #wcws=Weibo_CWS()
    #for line,std in zip(open("training.1.raw"),open("training.1.result")):
    #    line=line.strip()
    #    
    #    std=std.split()
    #    std=pre.gen_std(std)
    #    std=[t for _,t in sorted(list(std))]
    #    s=wcws(line)
    #    print(std)
    #    print(len(s),len(std))
    #    assert(len(s)==len(std))

