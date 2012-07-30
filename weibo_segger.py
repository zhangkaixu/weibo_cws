from isan.tagging.inc_segger import *
import sys
import pre
import thulac
import math
class DiffToHTML:
    """
    用于生成HTML的diff文件的插件
    """
    def __init__(self,filename):
        self.html=open(filename,'w')
        self.line_no=0
    def __del__(self):
        self.html.close()
    def to_set(self,seq):
        offset=0
        s=set()
        for w in seq:
            s.add((offset,w))
            offset+=len(w)
        return s
    def __call__(self,std,rst):
        self.line_no+=1
        std=self.to_set(std)
        rst=self.to_set(rst)
        #for b,w,t in std:
        #print(std)
        cor=std&rst
        seg_std={(b,w)for b,w in std}
        seg_rst={(b,w)for b,w in rst}
        if len(cor)==len(std):return
        html=[]
        for b,w in sorted(rst):
            if (b,w) in seg_std:
                html.append(w)
                continue
            html.append("<font color=red>"+w+"</font>")
        print(' '.join(html),"<br/>",file=self.html)
        html=[]
        for b,w in sorted(std):
            if (b,w) in rst:
                html.append(w)
                continue
            html.append("<font color=blue>"+w+"</font>")
        print(' '.join(html),"<br/><br/>",file=self.html)
        
class Default_Features :
    def __init__(self):
        self.thulac=thulac.Predict_C()
        self.chinese_characters=set(chr(i) for i in range(ord('一'),ord('鿋')+1))
        self.numbers=set()
        for c in '0123456789':
            self.numbers.add(c)
            self.numbers.add(chr(ord(c)+65248))
        self.latin=set()
        for c in 'abcdefghijklmnopqrstuvwxyz':
            self.latin.add(c)
            self.latin.add(chr(ord(c)+65248))
        #print(self.numbers)
        self.punks=set('…。，？：；！/.')
        self.idioms=set()
        for ln,line in enumerate(open("res/idiom.txt")):
            ol=line
            line=line.split()
            if line:
                self.idioms.add(line[0])

        self.sww=set()
        self.sww_pre=set()
        for line in open("res/sww_idiom.txt"):
            line=line.strip()
            self.sww.add(line.strip)
            for i in range(1,len(line)):
                self.sww_pre.add(line[:i])
            
        self.sms=set()
        for line in open("res/sms.txt"):
            line=line.strip()
            self.sms.add(line)

        self.sms_dict=dict()
        for line in open("res/sms_dict.txt"):
            word,freq,*dicts=line.split()
            dicts=[int(x)for x in dicts]
            freq=int(freq)

            self.sms_dict[word]=[freq,dicts]


    def set_raw(self,raw):
        """
        对需要处理的句子做必要的预处理（如缓存特征）
        """
        self.raw=raw
        self.raw_type=['##','##','##']
        for ch in self.raw:
            if ch in self.chinese_characters:
                self.raw_type.append('CC')
            elif ch in self.punks:
                self.raw_type.append('PU')
            elif ch in self.latin:
                self.raw_type.append('LT')
            elif ch in self.numbers:
                self.raw_type.append('NM')
            else:
                self.raw_type.append(ch)
        self.raw_type+=['##','##']
        self.uni_chars=list('###'+raw+'##')
        self.bi_chars=[(self.uni_chars[i],self.uni_chars[i+1]) 
                for i in range(len(self.uni_chars)-1)]

        #'''#set thulac related features'''
        thulac_result=self.thulac(raw,self.candidates)
        #for wt in thulac_result:
        #    if len(wt[0])==1:
        #        wt[1]+='1'
        self.lac_seq=[['s',None,thulac_result[0][1],None]]
        for i,wt in enumerate(thulac_result):
            w,t=wt
            if i-1>=0:
                lw,lt=thulac_result[i-1]
                if len(lw)==1 and lt=='np' and t=='np':
                    #print(lw,w)
                    self.lac_seq[-1][3]=True
            self.lac_seq[-1][2]=t
            for i in range(len(w)-1):
                self.lac_seq.append(['c',t,t,None])
                #if i==0:
                #    if self.lac_seq[-1][1]:
                #        self.lac_seq[-1][1]+='0'
            self.lac_seq.append(['s',t,None,None])
        #print(self.lac_seq)
        #if any(x[3] for x in self.lac_seq):
        #    for c,x in zip(raw,self.lac_seq):
        #        print(c,x)
        #    print(' ')
        #    input()

        if 0:
            print(raw)
            print(thulac_result)
            print(self.lac_seq)
            input()

    def __call__(self,span):
        raw=self.raw
        uni_chars=self.uni_chars
        bi_chars=self.bi_chars
        c_ind=span[0]+2
        ws_current=span[1]
        ws_left=span[2]
        pos=span[0]
        fv=[
                ("ws",ws_left,ws_current),
                ("c",uni_chars[c_ind],ws_current),
                ("r",uni_chars[c_ind+1],ws_current),
                ('l',uni_chars[c_ind-1],ws_current),
                ("cr",bi_chars[c_ind],ws_current),
                ("lc",bi_chars[c_ind-1],ws_current),
                
                ("rr2",bi_chars[c_ind+1],ws_current),
                ("l2l",bi_chars[c_ind-2],ws_current),
            ]
        fv+=[   ('L','c' if self.lac_seq[pos][0]=='c' else self.lac_seq[pos][3]),
                ('Ll',self.lac_seq[pos][0],self.lac_seq[pos][1]),
                ('Lr',self.lac_seq[pos][0],self.lac_seq[pos][2]),
                #('L3',self.lac_seq[pos][0],self.lac_seq[pos][3]),
                #('Llr',pos>0 and self.lac_seq[pos-1][0]=='s' and self.lac_seq[pos][0]=='s' and self.lac_seq[pos][1]=='np' and self.lac_seq[pos][2]=='np'),
                ]
        fv+=[   
                ('Tc',self.raw_type[c_ind]),
                ('Tl',self.raw_type[c_ind-1]),
                ('Tr',self.raw_type[c_ind+1]),
                ('Tlc',self.raw_type[c_ind-1],self.raw_type[c_ind]),
                ('Tcr',self.raw_type[c_ind],self.raw_type[c_ind+1]),
                ]
            

        if len(span)>=4:
            w_current=raw[span[0]-span[3]:span[0]]
            fv.append(("w",w_current))
            fv.append(("wi",w_current in self.idioms))
            fv.append(("wsww",w_current in self.sww))
            fv.append(("wssm",w_current in self.sms,self.lac_seq[pos][1]))
            if len(w_current)>1 and w_current in self.sww_pre:
                fv.append(("winswwpre",len(w_current)))
                #print(w_current)
            else:
                fv.append(("wnotswwpre",))

            dict_info=self.sms_dict.get(w_current,[0,[0,0,0,0,0,0,0,0]])
            #fv.append(('d-',len(w_current),w_current in self.sms_dict))
            fv.append(('d-f',len(w_current),math.floor(math.log(dict_info[0]+1))))
            fv.append(('d-0',len(w_current),dict_info[1][0]))
            fv.append(('d-1',len(w_current),dict_info[1][1]))
            fv.append(('d-2',len(w_current),dict_info[1][2]))
            fv.append(('d-3',len(w_current),dict_info[1][3]))
            fv.append(('d-4',len(w_current),dict_info[1][4]))
            fv.append(('d-5',len(w_current),dict_info[1][5]))
            fv.append(('d-6',len(w_current),dict_info[1][6]))
            #fv.append(('d-7',len(w_current),dict_info[1][7]))
        return fv
class Segmentation_Stats(perceptrons.Base_Stats):
    def __init__(self,actions,features):
        self.actions=actions
        self.features=features
        #初始状态 (解析位置，上一个位置结果，上上个位置结果，当前词长)
        self.init=(0,'|','|',0,0)
    def gen_next_stats(self,stat):
        """
        由现有状态产生合法新状态
        """
        ind,last,_,wordl,lwordl=stat
        yield 's',(ind+1,'s',last,1,wordl)
        yield 'c',(ind+1,'c',last,wordl+1,lwordl)

    def _actions_to_stats(self,actions):
        stat=self.init
        for action in actions:
            yield stat
            ind,last,_,wordl,lwordl=stat
            if action=='s':
                stat=(ind+1,'s',last,1,wordl)
            else:
                stat=(ind+1,'c',last,wordl+1,lwordl)
        yield stat

class Segmentation_Space(perceptrons.Base_Decoder):
    """
    线性搜索
    value = [alphas,betas]
    alpha = [score, delta, action, link]
    """
    def debug(self):
        """
        used to generate lattice
        """
        self.searcher.backward()
        sequence=self.searcher.sequence
        for i,d in enumerate(sequence):
            for stat,alpha_beta in d.items():
                if alpha_beta[1]:
                    for beta,db,action,n_stat in alpha_beta[1]:
                        if beta==None:continue
                        delta=alpha_beta[0][0][0]+beta-self.searcher.best_score
                        if action=='s':
                            pass
    
    def __init__(self,beam_width=8):
        super(Segmentation_Space,self).__init__(beam_width)
        self.init_data={'alphas':[(0,None,None,None)],'betas':[]}
        self.features=Default_Features()
        self.actions=Segmentation_Actions()
        self.stats=Segmentation_Stats(self.actions,self.features)

    def search(self,raw):
        self.raw=raw
        #print(raw)
        #print(self.candidates)
        self.stats.candidates=self.candidates
        self.features.set_raw(raw)
        self.sequence=[{}for x in range(len(raw)+2)]
        self.forward()
        res=self.make_result()
        return res

    def gen_next(self,ind,stat):
        """
        根据第ind步的状态stat，产生新状态，并计算data
        """
        fv=self.features(stat)
        alpha_beta=self.sequence[ind][stat]
        beam=self.sequence[ind+1]
        for action,key in self.stats.gen_next_stats(stat):
            #print(ind,self.candidates[ind],action)
            if self.candidates:
                if self.candidates[ind]!=None and action!=self.candidates[ind]:
                    continue
            #print("pass",ind,self.candidates[ind],action)
            if key not in beam:
                beam[key]={'alphas':[],'betas':[]}
            value=self.actions[action](fv)
            beam[key]['alphas'].append((alpha_beta['alphas'][0][0]+value,value,action,stat))

    def make_result(self):
        """
        由alphas中间的记录计算actions
        """
        sequence=self.sequence
        result=[]
        item=sequence[-1][self.thrink(len(sequence)-1)[0]]['alphas'][0]
        self.best_score=item[0]
        ind=len(sequence)-2
        while True :
            if item[3]==None: break
            result.append(item[2])
            item=sequence[ind][item[3]]['alphas'][0]
            ind-=1
        result.reverse()
        return result
class Weibo_Model(perceptrons.Base_Model):
    """
    模型
    """
    def __init__(self,model_file,schema=None):
        """
        初始化
        """
        super(Weibo_Model,self).__init__(model_file,schema)
        self.codec=tagging_codec
        self.Eval=tagging_eval.TaggingEval
        self.pre=pre.Pre()
    def test(self,test_raw,test_result):
        """
        测试
        """
        eval=self.Eval([DiffToHTML('diff.html')])
        for line,std in zip(open(test_raw),open(test_result)):#迭代每个句子
            line=line.strip()
            std=std.split()
            y=std
            std=pre.gen_std(std)
            std=[t for _,t in sorted(list(std))]
            raw,s=self.pre(line)
            self.schema.candidates=s
            self.schema.features.candidates=s
            assert(len(s)==len(std))
            hat_y=self(raw)
            eval(y,hat_y)
        eval.print_result()#打印评测结果
    def train(self,training_raw,training_result,iteration=5):
        """
        训练
        """
        for it in range(iteration):#迭代整个语料库
            eval=self.Eval()#测试用的对象
            sn=0
            for line,std in zip(open(training_raw),open(training_result)):#迭代每个句子
                sn+=1
                #if sn%10==0:
                #    print('('+str(sn)+')',end='')
                #    sys.stdout.flush()
                line=line.strip()
                std=std.split()
                y=std
                std=pre.gen_std(std)
                std=[t for _,t in sorted(list(std))]
                raw,s=self.pre(line)
                self.schema.candidates=s
                self.schema.features.candidates=s
                
                assert(len(s)==len(std))
                
                _,hat_y=self._learn_sentence(raw,y)
                eval(y,hat_y)
            eval.print_result()#打印评测结果
        self.actions.average(self.step)

