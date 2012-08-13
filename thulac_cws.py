#!/usr/bin/python3
import subprocess
import sys
import os
import pre


class Predict_C:
    def __init__(self,model_path='thulac/models/pku/cws_model_c'):# b m e s = 1 2 4 8
        self.poc_map={(None,None):'f',
                (None,'s'):'c',#e s
                (None,'c'):'3',#b m
                ('s',None):'9',# b s
                ('s','s'):'8',#s
                ('s','c'):'1',#b
                ('c',None):'6',#me
                ('c','s'):'4',#e
                ('c','c'):'2',#m
                }
        self.pre=pre.Pre()
        self.sp=subprocess.Popen(['./thulac/bin/predict_c',model_path,'-p']
                                        ,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        #result=self.sp.stdout.readline().decode().strip()
        #print(">>",result)
    def __call__(self,raw):
        #self.pre(raw)
        raw,cands=self.pre(raw)
        pocs=[]
        for i in range(len(cands)-1):
            pocs.append(self.poc_map[(cands[i],cands[i+1])])
        pocs=''.join(pocs)
        self.sp.stdin.write((pocs+' '+raw+'\n').encode())
        #print(pocs+' '+raw+'\n')
        self.sp.stdin.flush()
        result=self.sp.stdout.readline().decode().strip()
        #print(result)
        return result.split()


if __name__ == '__main__':
    model=Predict_C()
    for line in sys.stdin:
        r=model(line)
        print(' '.join(r))

