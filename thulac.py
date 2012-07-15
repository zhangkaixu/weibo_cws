#!/usr/bin/python3
import subprocess
import sys
import os


class Predict_C:
    def __init__(self):
        self.sp=subprocess.Popen(['./thulac/bin/predict_c','thulac/models/pku/model_c']
                                        ,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    def __call__(self,raw):
        self.sp.stdin.write((raw+'\n').encode())
        self.sp.stdin.flush()
        result=self.sp.stdout.readline().decode().strip()
        res=[]
        for item in result.split():
            word,_,tag=item.rpartition('_')
            res.append([word,tag])

        return res


if __name__ == '__main__':
    model=Predict_C()
    r=model('鱼上钩了，那是因为鱼爱上了渔夫，它愿用生命来博渔夫一笑。')
    print(r)

