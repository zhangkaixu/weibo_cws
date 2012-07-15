#!/usr/bin/python3
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
    def __call__(self,raw):
        """
        输入生句子，输出部分可以确定的切分结果
        """
        raw=raw.split()
        sen=''.join(raw)
        s=set()
        s=dict()
        offset=0
        for piece in raw:
            s[offset]='s'
            if piece.startswith("http://t.cn/"):
                for i in range(1,len(piece)):
                    s[offset+i]='c'
            for i,x in enumerate(piece):
                if x in '【】[]《》\'()（），、；“”~？！#@':
                    s[offset+i]='s'
                    s[offset+i+1]='s'
            for i in range(len(piece)-1):
                if piece[i] in '0123456789' and piece[i+1] in '0123456789':
                    s[offset+i+1]='c'
                if piece[i] in self.latin and piece[i+1] in self.latin:
                    s[offset+i+1]='c'
            s[offset+len(piece)]='s'
            offset+=len(piece)
        s[0]='s'
        s[len(sen)]='s'
        s=[s.get(i,None) for i in range(len(sen)+1)]
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
