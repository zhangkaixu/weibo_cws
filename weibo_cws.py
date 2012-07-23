#!/usr/bin/python3
import pre
import isan.tagging.inc_segger
import weibo_segger


"""
CWS model for weibo

input: weibo
output: segmented weibo

using a rule based preprosess and an incremental CWS model
"""


class Weibo_CWS:
    def __init__(self):
        self.pre=pre.Pre()
        pass
    def __call__(self,raw):
        sen,s=self.pre(raw)
        print(sen)
        print(s)
        return s
if __name__ == '__main__':
    model=weibo_segger.Weibo_Model("model.bin",weibo_segger.Segmentation_Space(beam_width=8))
    model.train("training.1.raw","training.1.result",10)
    model.test("test.1.raw","test.1.result")



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

