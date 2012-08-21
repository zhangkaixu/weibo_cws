#!/usr/bin/python3
import re
import isan.common.Chinese as Chinese
class Pre:
    """
    使用基于规则的方法
    预处理微博
    """
    def __init__(self):
        self.latin=set()
        for i in range(ord('a'),ord('z')+1):
            self.latin.add(chr(i))
        for i in range(ord('A'),ord('Z')+1):
            self.latin.add(chr(i))
        self.digit=set()
        for i in range(ord('0'),ord('9')+1):
            self.digit.add(chr(i))
        #print(self.digit)
        self.html=re.compile(r'''http://t\.cn/[0-9a-zA-Z]+''')
    def __call__(self,raw):
        """
        输入生句子，输出部分可以确定的切分结果
        """
        raw=raw.split()
        sen=''.join(raw)
        #print(raw)
        s=set()
        s=dict()
        offset=0
        for piece in raw:
            s[offset]='s'
            if piece.startswith("http://t.cn/"):#deal with urls
                #print('start')
                #input()
                for i in range(1,len(piece)):
                    if i<12 or piece[i] in self.latin or piece[i] in self.digit:
                        s[offset+i]='c'
                    else:
                        s[offset+i]='s'
                        #print('end',s[offset+i],offset+i)
                        break
            else:
                for i,x in enumerate(piece): # deal with puncs that should always be separated
                    if x in '【】[]《》\'()（），、；“”~？！#@|':
                        s[offset+i]='s'
                        s[offset+i+1]='s'
                for i in range(len(piece)-1):# deal with digit or latin sequence
                    if piece[i] in '0123456789' and piece[i+1] in '0123456789':
                        s[offset+i+1]='c'
                    if piece[i] in self.latin and piece[i+1] in self.latin:
                        s[offset+i+1]='c'
                #for i in range(len(piece)-1): # deal with -
                #    if piece[i]=='-' and piece[i+1]=='-':
                #        s[offset+i+1]='c'

                stat=0
                for i in range(len(piece)): # deal with ... and ......
                    if piece[i]=='.':
                        stat+=1
                    else:
                        if stat==2:
                            s[offset+i-1]='s'
                        if stat==3:
                            s[offset+i-1]='c'
                            s[offset+i-2]='c'
                        if stat==4:
                            s[offset+i-1]='s'
                            s[offset+i-2]='c'
                            s[offset+i-3]='c'

                        if stat==5:
                            s[offset+i-1]='s'
                            s[offset+i-2]='s'
                            s[offset+i-3]='c'
                            s[offset+i-4]='c'
                        if stat>=6:
                            s[offset+i-1]='c'
                            s[offset+i-2]='c'
                            s[offset+i-3]='c'
                            s[offset+i-4]='c'
                            s[offset+i-5]='c'

                        if stat>1:s[offset+i]='s'
                        stat=0
                # deal with ^_^ ^0^ ^o^ !!
            for mo in self.html.finditer(piece):
                break
                #print(s.get(offset+mo.start(),None),'s')
                #print(s.get(offset+mo.end(),None),'s')
                #s[offset+mo.start()]='s'
                #s[offset+mo.end()]='s'
                for i in range(mo.start()+1,mo.end()):
                    #print(s.get(offset+i,None),'c')
                    s[offset+i]='c'
                #print(mo.group(0),mo.start(),mo.end())
                #print(piece[mo.start():mo.end()],mo.group(0))
            s[offset+len(piece)]='s'
            offset+=len(piece)
        s[0]='s'
        s[len(sen)]='s'
        s=[s.get(i,None) for i in range(len(sen)+1)]
        #print(sen)
        #print(Chinese.to_full(sen))
        #sen=Chinese.to_full(sen)
        return sen,s # 返回生句子，以及分、合约束


def gen_std(std):
    s=set()
    offset=0
    for word in std:
        s.add((offset,'s'))
        if '#' in word and len(word)>1:
            print(word)
        for i in range(1,len(word)):
            s.add((offset+i,'c'))
        s.add((offset+len(word),'s'))
        offset+=len(word)
    return s
if __name__ == '__main__':
    pre=Pre()
    nstd,nrst,ncor=0,0,0
    for line,std in zip(open("training.raw"),open("training.result")):
        line=line.strip()
        std=std.split()
        raw=''.join(line.split())
        std_s=gen_std(std)
        sen,rst_s=pre(line)
        rst_s={(i,x) for i,x in enumerate(rst_s) if x!=None}
        nstd+=len(std_s)
        nrst+=len(rst_s)
        ncor+=len(std_s&rst_s)
        for r in rst_s:
            if r not in std_s:
                print(std)
                print(r,raw[r[0]])

    print(nstd,nrst,ncor)
    p=ncor/nrst
    r=ncor/nstd
    print(p,r,2*p*r/(p+r))

    pass
