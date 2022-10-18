import pickle
import random
from random import shuffle

sum_card = 110#卡的上限
pickle_file2 = open('Rank_mns.pkl','rb')
Rank_mns = pickle.load(pickle_file2)
pickle_file2.close()
Rank_amount = [0,18,15,13,11,9,6]#不同等级的数量

#BOB类
class Bob():
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Bob, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    #公用卡池
    store = [0]*sum_card
    def __init__(self):
        self.bd_mns = []

    def halo_buff_update(self):
        pass

    #刷新卡库，准备游戏
    def begin(self,date):
        self.store = []
        for i in range(len(date)):
            tempt = Rank_amount[int(date[i][1])]
            self.store.append(tempt)
        #shuffle(self.store)

    #摧毁卡池
    def destory(self):
        self.store = [0]*sum_card

    #抽取n张rank等级以下的卡
    def draw(self,n,rank):
        res = []
        for i in range(n):
            res.append(self.draw_one(rank))
        return res

    def draw_one(self,rank):
        tempt = 0
        for i in range(Rank_mns[rank]):
            tempt += self.store[i]
        rnd = random.random() * tempt
        for i, w in enumerate(self.store):
            rnd -= w
            if rnd < 0:
                self.store[i]-=1
                return i

    #放回卡
    def draw_back_one(self,card):
        self.store[card] += 1
                
    def draw_back(self,card):
        for i in range(len(card)):
            if card[i] != None:
                self.store[card[i]] += 1
