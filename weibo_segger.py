from isan.tagging.inc_segger import *
import sys
import pre
import thulac
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
        self.punks=set('…。，？：；！/')
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
            else:
                self.raw_type.append(ch)
        self.raw_type+=['##','##']
        self.uni_chars=list('###'+raw+'##')
        self.bi_chars=[(self.uni_chars[i],self.uni_chars[i+1]) 
                for i in range(len(self.uni_chars)-1)]

        #set thulac related features
        thulac_result=self.thulac(raw)
        #print(thulac_result)
        self.lac_seq=[['s',None,thulac_result[0][1]]]
        for w,t in thulac_result:
            self.lac_seq[-1][-1]=t
            for i in range(len(w)-1):
                self.lac_seq.append(['c',t,t])
                if i==0:
                    self.lac_seq[-1][1]+='0'
            self.lac_seq.append(['s',t,None])
        #print(self.lac_seq)

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
        #print(raw)
        #print(len(raw))
        #print(c_ind)
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
        fv+=[   ('L',self.lac_seq[pos][0]),
                ('Ll',self.lac_seq[pos][0],self.lac_seq[pos][1]),
                ('Lr',self.lac_seq[pos][0],self.lac_seq[pos][2]),
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
            fv.append(("wssm",w_current in self.sms))
            if len(w_current)>1 and w_current in self.sww_pre:
                fv.append(("winswwpre",len(w_current)))
                #print(w_current)
            else:
                fv.append(("wnotswwpre",))
        return fv
class Segmentation_Stats(perceptrons.Base_Stats):
    def __init__(self,actions,features):
        self.actions=actions
        self.features=features
        #初始状态 (解析位置，上一个位置结果，上上个位置结果，当前词长)
        self.init=(0,'|','|',0)
    def gen_next_stats(self,stat):
        """
        由现有状态产生合法新状态
        """
        ind,last,_,wordl=stat
        yield 's',(ind+1,'s',last,1)
        yield 'c',(ind+1,'c',last,wordl+1)

    def _actions_to_stats(self,actions):
        stat=self.init
        for action in actions:
            yield stat
            ind,last,_,wordl=stat
            if action=='s':
                stat=(ind+1,'s',last,1)
            else:
                stat=(ind+1,'c',last,wordl+1)
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
                assert(len(s)==len(std))
                
                _,hat_y=self._learn_sentence(raw,y)
                eval(y,hat_y)
            eval.print_result()#打印评测结果
        self.actions.average(self.step)

