from abc import abstractclassmethod,ABCMeta
import abc
from random import shuffle
import random
import json
import copy
from bob import *
import xlrd
import xlwt
import pickle

data_hero = xlrd.open_workbook('dateHero.xlsx')
table_hero = data_hero.sheets()[0]
hero_data = []
for i in range(1,len(table_hero.col_values(0))):
    hero_data.append(table_hero.row_values(i))
pickle_file = open('mon_data.pkl','rb')
mon_data = pickle.load(pickle_file)
pickle_file.close()
#不同等级的编号
proper_begin_number = 14#属性的起始序号
Minions_limit = 7
Card_limit = 10
Fee_limit = 10#钱的上限
Rank_limit = 6#等级上限
property_name = ['圣盾','嘲讽','剧毒','风怒','复生','磁力','魔免','无视','体积']#属性

#玩家类----------------------------------------------
class Player():
    mn_limit = Minions_limit
    cd_limit = Card_limit
    fee_limit = Fee_limit
    rank_limit = Rank_limit
    def __init__(self,hero):
        self.cd_mns = []#card手牌
        self.bd_mns = []#场上的怪兽
        self.store_mns = []#可以购买的牌
        self.dead_mns = []#死亡过的随从
        self.w_roar_used = []#发动过的战吼
        self.d_r_used = []#发动过的亡语
        self.__turn_fee = 3#每回合给的费用
        self.fee = self.__turn_fee#费用
        self.freeze = False#冻结
        self.mns_fee = 3#买怪的钱
        self.cell_fee = 1#卖怪的钱
        self.cell_amount = [3,4,4,5,5,6]#商店刷怪数量
        self.game = None
        self.bob = Bob()#bob
        self.opponent = self.bob#对手
        self.last_opponent = []#上一个对手的随从
        self.hero = Hero(self,hero)
        self.win_flag = False
        self.turn_state = 0
        
        self.w_r_time = 1
        self.d_r_time = 1
        self.s_m_time = 1

    @property
    def rank(self):
        return self.hero.rank
    
    @rank.setter
    def rank(self,value):
        self.hero.rank = value

    @property
    def blood(self):
        return self.hero.blood
        
    @property
    def rank_fee(self):#等级花费
        return self.hero.rank_fee
    
    @property
    def rank_fee_curent(self):
        return self.hero.rank_fee_curent

    @rank_fee_curent.setter
    def rank_fee_curent(self,value):
        self.hero.rank_fee_curent = value

    def up_rank(self):
        if self.fee>=self.rank_fee_curent:
            self.rank += 1
            self.fee -= self.rank_fee_curent
            self.rank_fee_curent = self.rank_fee
            return True
        else:
            return False

    #每回合给的费用
    @property
    def turn_fee(self):
        return self.__turn_fee

    @turn_fee.setter
    def turn_fee(self,value):
        self.__turn_fee = value
        if self.__turn_fee<0:
            self.__turn_fee=0
        elif self.__turn_fee>10:
            self.__turn_fee = 10

    #场上怪物的体积总和
    def size(self):
        res = 0
        for i in range(len(self.bd_mns)):
            if self.bd_mns[i].proper_value(8) ==1:
                res+=1
        return res

    def full_mns(self):
        if self.size() < self.mn_limit:
            return False
        else:
            return True

    def card_len(self):
        return len(self.cd_mns)

    def next_position(self,position,owner = None):
        self.change_position(position,self.next_position_show(position,owner))

    def next_position_show(self,position,owner = None):
        target = position+1
        len_bd = len(self.bd_mns)
        count = 0
        while True:
            count += 1
            if target >= len_bd:
                target = 1
            if self.bd_mns[target].proper_value(7)!=1:
                break
            elif count > len_bd:
                break
            target += 1
        return target

    def change_position(self,position,target,owner = None):
        self.bd_mns.insert(target,self.bd_mns.pop(position))

    #使用手牌第n个怪
    def use(self,n,position,target = None):
        self.summon(n,position,target)

    def summon(self,n,position,target = None):
        mns = self.cd_mns.pop(n)
        mns.proper[7] = 1
        mns.change_flag = False
        if mns.proper[5] == 1:
            if self.bd_mns[position].race == mns.race:
                self.bd_mns[position].magnetic(mns)
                return True
        if self.pull_in(self,mns,position):
            #对原来的随从,而不是他
            for w_r in range(self.w_r_time):
                if target == None:
                    self.effect(mns.war_roar,position)
                else:
                    if target >= position:
                        target += 1
                    self.effect(mns.war_roar,position,target)
            if type(mns.war_roar) == dict:
                self.w_roar_used.append(mns.card_id)
            self.listen_phrase('summon',position,mns)
            if type(mns.war_roar) == dict:
                self.listen_phrase('w_roar',position,mns)
                
            mns.proper[7] = 0
            self.halo_buff_update()
            return True
        else:
            self.cd_mns.insert(n,mns)
            self.cd_mns[n].proper[7] = 0
            self.halo_buff_update()
            return False

    #置入战场，不触发战吼
    def pull_in(self,owner,mns,position):
        flag = False
        for s_m in range(self.s_m_time):
            if self.full_mns() and mns.proper[8] == 1:
                pass
            else:
                owner.bd_mns.insert(position,mns)
                flag = True
        if flag:
            self.halo_buff_update()
            self.listen_phrase('pull_in',position,mns)
        self.mns_3_combine()
        return flag

    #买第n个怪
    def buy(self,n):
        if self.fee>=self.mns_fee and len(self.cd_mns)<self.cd_limit:
            self.fee -= self.mns_fee
            mns = self.store_mns.pop(n)
            self.cd_mns.append(mns)
            self.listen_phrase('buy','none',mns)
            self.mns_3_combine()
        else:
            return False

    #卖第n个怪
    def cell(self,n):
        mns = self.bd_mns[n]
        tempt_id = mns.card_id
        self.bd_mns.pop(n)
        self.halo_buff_update()
        self.listen_phrase('cell','none',mns)
        
        self.bob.draw_back_one(tempt_id)
        self.fee += self.cell_fee
        self.mns_3_combine()
        return True
            #self.fee += self.cell_fee
            #self.bob.draw_back_one(tempt_id)
            #self.halo_buff_update()

    def mns_3_combine(self):
        if self.turn_state == 0:
            tempt_card_id = {}
            result = False
            for i in range(len(self.cd_mns)):
                if self.cd_mns[i].gold == 0:
                    if self.cd_mns[i].card_id in tempt_card_id:
                        tempt_card_id[self.cd_mns[i].card_id].append(i)
                    else:
                        tempt_card_id[self.cd_mns[i].card_id] = []
                        tempt_card_id[self.cd_mns[i].card_id].append(i)

            for i in range(len(self.cd_mns),len(self.cd_mns)+len(self.bd_mns)):
                if self.bd_mns[i-len(self.cd_mns)].gold == 0:
                    if self.bd_mns[i-len(self.cd_mns)].card_id in tempt_card_id:
                        tempt_card_id[self.bd_mns[i-len(self.cd_mns)].card_id].append(i)
                    else:
                        tempt_card_id[self.bd_mns[i-len(self.cd_mns)].card_id] = []
                        tempt_card_id[self.bd_mns[i-len(self.cd_mns)].card_id].append(i)
                    
            for i in tempt_card_id:
                if len(tempt_card_id[i]) >= 3:        
                    if tempt_card_id[i][2] < len(self.cd_mns):
                        mns2 = self.cd_mns[tempt_card_id[i][2]]
                        self.cd_mns.pop(tempt_card_id[i][2])
                    else:
                        mns2 = self.bd_mns[tempt_card_id[i][2]-len(self.cd_mns)]
                        self.bd_mns.pop(tempt_card_id[i][2]-len(self.cd_mns))
                    if tempt_card_id[i][1] < len(self.cd_mns):
                        mns1 = self.cd_mns[tempt_card_id[i][1]]
                        self.cd_mns.pop(tempt_card_id[i][1])
                    else:
                        mns1 = self.bd_mns[tempt_card_id[i][1]-len(self.cd_mns)]
                        self.bd_mns.pop(tempt_card_id[i][1]-len(self.cd_mns))
                    if tempt_card_id[i][0] < len(self.cd_mns):
                        mns = self.cd_mns[tempt_card_id[i][0]]
                        self.cd_mns.pop(tempt_card_id[i][0])
                    else:
                        mns = self.bd_mns[tempt_card_id[i][0]-len(self.cd_mns)]
                        self.bd_mns.pop(tempt_card_id[i][0]-len(self.cd_mns))
                    mns.golden([mns1,mns2])
                    self.cd_mns.append(mns)
                    result = True
            if result:
                self.mns_3_combine()
        

    #开始战斗
    def battle_begin(self):
        self.halo_buff_update()
        self.turn_state = 1
        self.listen_phrase('battle_begin','none')

    def battle_over(self):
        self.turn_state = 0
        self.listen_phrase('battle_over','none')

    def turn_over(self):
        self.listen_phrase('turn_over','none')

    #下一回合
    def next_turn(self):
        for i in range(len(self.cd_mns)):
            self.change(self.cd_mns[i])
        self.halo_buff_update()
        self.turn_fee+=1
        self.fee = self.turn_fee
        self.refresh_free()
        self.rank_fee_curent -= 1
        self.listen_phrase('next_turn','none')
        if self.win_flag:
            self.listen_phrase('next_turn_win','none')
        else:
            self.listen_phrase('next_turn_lose','none')
        self.mns_3_combine()

    def freezen(self):
        self.freeze = not self.freeze
        return self.freeze
    
    def get_refresh_amount(self):
        return self.cell_amount[self.rank-1]

    def draw_back(self):
        card_list = []
        for i in range(len(self.store_mns)):
            card = self.store_mns[i].card_id
            card_list.append(card)
        self.bob.draw_back(card_list)
        self.store_mns = []

    def refresh_free(self):
        card_list = []
        if self.freeze:
            self.freeze = False
            if len(self.store_mns)<self.get_refresh_amount():
                card_list = self.bob.draw(self.get_refresh_amount()-len(self.store_mns),self.rank)
                for i in range(len(card_list)):
                    card = Minions(self,card_list[i])
                    self.store_mns.append(card)
        else:
            self.draw_back()
            card_list = self.bob.draw(self.get_refresh_amount(),self.rank)
            for i in range(len(card_list)):
                card = Minions(self,card_list[i])
                self.store_mns.append(card)
    
    #刷新卡
    def refresh(self):
        if self.fee>0:
            self.draw_back()
            self.store_mns = []
            card_list = self.bob.draw(self.get_refresh_amount(),self.rank)
            for i in range(len(card_list)):
                card = Minions(self,card_list[i])
                self.store_mns.append(card)
            self.fee -= 1
            return True
        else:
            return False

#--------------------------------------------------
        
    def listen_phrase(self,value,position,mns='none'):
        if mns == 'none' or mns.proper[7] != 1:
            if value == 'shield_lose':
                self.listen_phrase_text('shield_lose',position,mns)
            elif value == 'pull_in':
                self.listen_phrase_text('pull_in',position,mns)
            elif value == 'next_turn':
                self.listen_phrase_text('next_turn',position,mns)
            elif value == 'next_turn_win':
                self.listen_phrase_text('next_turn_win',position,mns)
            elif value == 'next_turn_lose':
                self.listen_phrase_text('next_turn_lose',position,mns)
        else:
            self.listen_phrase_text(value,position,mns)

    def listen_phrase_text(self,listen_type,position,mns):
        if mns == 'none':
            race = '*'
            proper = '*'
            owner = self
        else:
            proper = mns.proper
            race = mns.race
            owner = mns.owner
        for i in range(len(owner.bd_mns)):
            if type(owner.bd_mns[i].listener) == dict:
                self.listen_phrase_text_effect(listen_type,mns.listener,position,owner.bd_mns[i])
                
        owner = owner.opponent
        if type(owner) != Bob:
            for i in range(len(owner.bd_mns)):
                if type(owner.bd_mns[i].listener) == dict:
                    self.listen_phrase_text_effect(listen_type,mns.listener,position,owner.bd_mns[i])                                  

        def listen_phrase_text_effect(self,listen_type,text,position,mns):
            if text['listen_type'] == 'listen' or text['listen_type'] == self.turn_state:
                if mns.proper[7] != 1:
                    if text['pointOrNot'][1] == 'owner':
                        if text['listen_type'] == listen_type:
                            if text['race'] == '-' or race == '*' or text['race'] == race:
                                for k in range(len(text['property'])):
                                    if text['property'][k] == '-' or proper == '*' or bool(mns.proper_name(text['property'][k])):
                                        for j in range(len(text['value'])):
                                            if text['pointOrNot'][0] == 'point':
                                                self.effect(text['value'][j],position,i)
                                            else:
                                                self.effect(text['value'][j],i,position)

            if len(mns.listener['other'])>0:
                self.listen_phrase_text_effect(listen_type,text['other'],position,mns)

        
#--------------------------------------------------
        
    def munual(self,n):
        if self.cd_mns[n].war_roar != 0:
            if self.cd_mns[n].war_roar['pointOrNot'][1] == 1:
                if len(self.all_suitable(self,self.cd_mns[n].war_roar['race'],self.cd_mns[n].war_roar['property'])) !=0:
                    return True
        return False
    
    def effect(self,phrase,position,target='none'):
        if type(phrase) == dict:
            self.effect_text(phrase,position,target)
            if 'other' in phrase:
                for i in range(len(phrase['other'])):
                    self.effect(phrase['other'][i],position,target)
        
    def effect_text(self,phrase,position,target='none'):
        if position == 'owner':
            return True
        text = copy.deepcopy(phrase)
        #转换拥有者
        if text['pointOrNot'][1]=='owner' or text['pointOrNot'][1]=='all' or text['pointOrNot'][1]=='random' or text['pointOrNot'][1]=='side':
            owner = self
        elif text['pointOrNot'][1]=='opponent'or text['pointOrNot'][1]=='opponent_all' or text['pointOrNot'][1]=='random_opponent' or text['pointOrNot'][1]=='opponent_side':
            owner = self.opponent
        elif text['pointOrNot'][1]=='opponent_left':
            owner = self.opponent
        elif text['pointOrNot'][1]==1:
            owner = self
        elif text['pointOrNot'][1]=='this' or text['pointOrNot'][1]=='left':
            owner = self
        else:
            owner = self       
        #转换价值
        for i in range(len(text['value'])):
            if i>=2:
                break
            if type(text['value'][i]) == str:
                if text['value'][0] == 'dead_mns':
                    tempt_list = []
                    tempt_text = {}
                    tempt_text['race'] = text['race']
                    tempt_text['property'] = text['property']
                    tempt_text['rank'] = '-'
                    while True:
                        for mns_check in range(len(self.dead_mns)):
                            if self.random_suitable_mondata_plus(self.dead_mns[mns_check],tempt_text,position) != None:
                                tempt_list.append(self.dead_mns[mns_check])
                            if len(tempt_list) >= text['value'][1]:
                                break
                        break
                    text['value'][0] = tempt_list
                elif text['value'][i] == 'attk':
                    text['value'][i] = int(self.bd_mns[position].attk)
                elif text['value'][i] == 'blood':
                    text['value'][i] = int(self.bd_mns[position].blood_curent)
                elif text['value'][i] == 'lose_blood':
                    text['value'][i] = int(self.bd_mns[position].blood) - int(self.bd_mns[position].blood_curent)
                elif text['value'][i] == 'hero_blood':
                    text['value'][i] = int(owner.hero.blood_curent)
                elif text['value'][i] == 'lose_hero_blood':
                    text['value'][i] = int(owner.hero.blood) - int(owner.hero.blood_curent)
                elif text['value'][i] == 'rank':
                    text['value'][i] = int(self.bd_mns[position].rank)
                elif text['value'][i] == 'mns':
                    if 'self' in text['value'][3]:
                        if text['value'][3]['self'] == 1:
                            text['value'][i] = len(self.all_suitable(owner,text['value'][3]['race'],text['value'][3]['property']))
                        else:
                            text['value'][i] = len(self.all_suitable(owner,text['value'][3]['race'],text['value'][3]['property'],position))
                    else:
                        text['value'][i] = len(self.all_suitable(owner,text['value'][3]['race'],text['value'][3]['property'],position))
                elif text['value'][i] == 'opponent_mns':
                    text['value'][i] = len(self.all_suitable(owner.opponent,text['value'][3]['race'],text['value'][3]['property']))
                elif text['value'][i] == 'all_mns':
                    if 'self' in text['value'][3]:
                        if text['value'][3]['self'] == 1:
                            text['value'][i] = len(self.all_suitable(owner,text['value'][3]['race'],text['value'][3]['property']))
                        else:
                            text['value'][i] = len(self.all_suitable(owner,text['value'][3]['race'],text['value'][3]['property'],position))
                    else:
                        text['value'][i] = len(self.all_suitable(owner,text['value'][3]['race'],text['value'][3]['property'],position))
                    text['value'][i] += len(self.all_suitable(owner.opponent,text['value'][3]['race'],text['value'][3]['property']))        
            elif type(text['value'][i]) == dict:
                text['value'][i] = self.random_suitable_mondata(text['value'][i],position)
        #简单的计算
        if len(text['value']) >= 3:
            text['value'][0] = text['value'][0]*text['value'][2]
            text['value'][1] = text['value'][1]*text['value'][2]
        #商店有关
        if text['pointOrNot'][1]=='store':
            if text['pointOrNot'][1]=='all' or text['pointOrNot'][1]=='opponent_all':
                target = []
                for i in range(len(self.store_mns)):
                    target.append(i)
            if text['type']=='change':
                self.change(self.store_mns[position],text['value'][0])
            elif text['type']=='buff':
                for i in range(len(self.store_mns)):
                    self.store_mns[i].buff(text['value'][0],text['value'][1])
            return True
        #转换对象
        if text['pointOrNot'][1]=='owner' or text['pointOrNot'][1]=='opponent':
            target = ['owner']
        elif text['pointOrNot'][1]=='all' or text['pointOrNot'][1]=='opponent_all':
            target = self.all_suitable(owner,text['race'],text['property'],position)
        elif text['pointOrNot'][1]=='random' or text['pointOrNot'][1]=='random_opponent':
            target = []
            target.append(self.random_suitable(owner,text['race'],text['property']))
        elif text['pointOrNot'][1]=='side':
            target = self.side_suitable(owner,text['race'],text['property'],position)
        elif text['pointOrNot'][1]=='opponent_side':
            target = self.side_suitable(owner,text['race'],text['property'],target)
        elif text['pointOrNot'][1]=='this':
            target = []
            target.append(position)
        elif text['pointOrNot'][1]=='opponent_left' or text['pointOrNot'][1]=='left':
            target = []
            target.append(self.left_suitable(owner,text['race'],text['property']))
        else:
            tempt = []
            tempt.append(target)
            target = tempt
        #执行
        if text['type']=='summon':
            if type(text['value'][0]) == list:
                for i in range(len(text['value'][0])):
                    self.token(owner,position+1,[text['value'][0][i],1])
            else:
                self.token(owner,position+1,text['value'])
        if text['type']=='summon_sp':
            if type(text['value'][0]) == list:
                for i in range(len(text['value'][0])):
                    self.token(owner,position+1,[text['value'][0][i],1],text['summon_sp'])
            else:
                self.token(owner,position+1,text['value'],text['summon_sp'])
        elif text['type']=='buff':
            self.buff_mns(owner,text['value'],target)
        elif text['type']=='property':
            self.set_proper(owner,text['value'],target)
        elif text['type']=='damage':
            self.damage(owner,self,position,text['value'][1],target)
        elif text['type']=='find':
            pass
        elif text['type']=='evolution':
            pass
        elif text['type']=='halo_buff':           
            self.halo_buff_set(owner,self,position,text['value'][:2],target)
        elif text['type']=='halo_immune':
            self.halo_immune_set(owner,text['value'][0],target)
        elif text['type']=='halo_war_roar':
            self.halo_w_r_set(owner,text['value'][0],target)
        elif text['type']=='halo_death_rattle':
            self.halo_d_r_set(owner,text['value'][0],target)
        elif text['type']=='halo_summon':
            self.halo_s_m_set(owner,text['value'][0],target)
        elif text['type']=='change':
            self.change(owner.bd_mns[position],text['value'][0])
        elif text['type']=='war_roar':
            self.w_roar_effect(owner.bd_mns[position],text['value'][0],position,target)
        elif text['type']=='buff_used':
            tempt_time = 0
            for w_r in range(len(self.w_roar_used)):
                if self.w_roar_used[w_r] == owner.bd_mns[position].card_id:
                    tempt_time+=1
            text['value'][0] *= tempt_time
            text['value'][1] *= tempt_time
            self.buff_mns(owner,text['value'],target)
        elif text['type']=='steal_last_opponent':
            self.steal(owner,text,position,target,self.last_opponent)
        elif text['type']=='steal':
            self.steal(owner,text,position,target)
        else:
            pass
        
    def steal(self,owner,phrase,position,target,list_mns):
        tempt_list = []
        #phrase['pointOrNot'][1][0]
        tempt_text = {}
        tempt_text['race'] = phrase['race']
        tempt_text['property'] = phrase['property']
        tempt_text['rank'] = '-'

        for i in range(len(list_mns)):
            if self.random_suitable_mondata_plus(list_mns[i].card_id,tempt_text,position) != None:
                tempt_list.append(list_mns[i].card_id)
        if len(tempt_list)> phrase['value'][1]:
            result = random.sample(tempt_list,phrase['value'][1])
        else:
            result = tempt_list
        for i in range(len(result)):
            mns = Minions(owner,result[i])
            print(owner.hero.name,'获得了',mns.name)
            owner.cd_mns.append(mns)
      
    #触发战吼
    def w_roar_effect(self,mns,value,position,target = None):
        if type(mns.war_roar) == dict:
            if mns.war_roar['pointOrNot'][1]=='all':
                for j in range(value):
                    self.effect(mns.war_roar,position,target[0])
            else:
                for j in range(value):
                    for i in range(len(target)):
                        if target[i] == None or target[i] == 'none':
                            self.effect(mns.war_roar,position)
                        else:
                            self.effect(mns.war_roar,position,target[i])
            self.listen_phrase('w_roar',position,mns)
            
    #改变卡
    def change(self,mns):
        mns.zerus(self.random_suitable_mondata({'race':'-','rank':'-','property':['-']}))

    #衍生物
    def token(self,owner,position,value,value1 = None):
        if value != None:
            print(owner.hero.name,'的',owner.bd_mns[position-1].name,'召唤了',value[1],'个',mon_data[value[0]][0],'...')
            for i in range(value[1]):
                token_Minions = Minions(owner,value[0])
                if value1 != None:
                    if value1['race'] != '-':
                        token_Minions.race = value1['race']
                    if value1['rank'] != '-':
                        token_Minions.rank = value1['rank']
                    for p in range(len(value1['property'])):
                        if value1['property'][p] != '-':
                            token_Minions.set_proper_name(value1['property'][p],1)
                owner.pull_in(owner,token_Minions,position)
            return True
    
    #buff
    def buff_mns(self,owner,value,target):
        for i in range(len(target)):
            if target[i] != 'none' and target[i] != None:
                if target[i] == 'owner':
                    pass
                else:
                    print('buff：',owner.bd_mns[target[i]].name,value[0],'/',value[1])
                    owner.bd_mns[target[i]].buff(value[0],value[1])

    #设置属性
    def set_proper(self,owner,value,target):
        for i in range(len(target)):
            if target[i] != 'none' and target[i] != None:
                if target[i] == 'owner':
                    pass
                else:
                    for j in range(len(value)):
                        owner.bd_mns[target[i]].set_proper_name(value[j],1)

    #owner接受伤害
    def damage(self,owner,owner1,position,value,target):
        if value != 0:
            if len(target) >= 1:
                if target[0] == 'owner':
                    owner.hero.damage_heal(value,'owner')
                elif target[0] == None or target[0] == 'none':
                    pass
                else:
                    blood = []
                    self_mns = []
                    posion_flag = owner1.bd_mns[position].proper[2]
                
                    for i in range(len(target)):
                        self_mns.append(owner.bd_mns[target[i]])
                        blood.append(owner.bd_mns[target[i]].blood_curent)
                    for i in range(len(self_mns)):
                        for j in range(len(owner.bd_mns)):
                            if owner.bd_mns[j] == self_mns[i]:
                                print(owner1.bd_mns[position].name,'对',self_mns[i].name,'造成',-value,'点damage')
                                self_mns[i].damage_heal(value,j)
                                
                    for i in range(len(self_mns)):
                        if self_mns[i].blood_curent <= 0:
                            owner.kill(self_mns[i])
                            self.effect(owner1.bd_mns[position].overkillean,position,target)
                        else:#剧毒
                            if posion_flag == 1:
                                if self_mns[i].blood_curent < blood[i]:
                                    owner.kill(self_mns[i])
                                    self.effect(owner1.bd_mns[position].overkillean,position,target)

    #所有匹配入口
    def suitable(self,owner,race,proper,target):
        for i in range(len(proper)):
            if proper[i] == '-' or bool(owner.bd_mns[target].proper_name(proper[i])):
                if race == '-' or race == owner.bd_mns[target].race or owner.bd_mns[target].race == '*':
                    if owner.bd_mns[target].proper[7] != 1:
                        return True
        return False

    #单独匹配
    def proper_name_match(self,name):
        for i in range(len(property_name)):
            if len(name) == 3:
                if property_name[i] == name[1:]:
                    return i
            else:
                if property_name[i] == name:
                    return i
        return None
    
    def random_suitable_mondata(self,text,position = None):
        tempt_value = []
        if position != None:
            if self.bd_mns[position].name == '??':
                tempt_value = []
            else:
                for c_id in range(len(mon_data)):
                    if self.random_suitable_mondata_plus(c_id,text,position) != None:
                        tempt_value.append(c_id) 
        else:
            for c_id in range(len(mon_data)):
                    if self.random_suitable_mondata_plus(c_id,text,position) != None:
                        tempt_value.append(c_id) 
        return random.choice(tempt_value)

    def random_suitable_mondata_plus(self,c_id,text,position = None):
            if mon_data[c_id][proper_begin_number+7] != 1:
                if text['race'] == '-' or mon_data[c_id][4] == text['race'] or mon_data[c_id][4] == '*':
                    if text['rank'] == '-' or mon_data[c_id][1] == text['rank'] or mon_data[c_id][1] == '*':
                        if mon_data[c_id][1] != 0:
                            for p in range(len(text['property'])):
                                pro = self.proper_name_match(text['property'][p])
                                if text['property'][p] == '-':
                                    return c_id
                                elif pro != None:
                                    if len(text['property'][p]) == 3:
                                        if mon_data[c_id][proper_begin_number+pro] == 0:
                                             return c_id
                                    else:
                                        if mon_data[c_id][proper_begin_number+pro] != 0:
                                             return c_id
                                else:
                                    if text['property'][p] == '战吼':
                                        if type(mon_data[c_id][6]) == dict:
                                             return c_id
                                    elif text['property'][p] == '亡语':
                                        if type(mon_data[c_id][7]) == dict:
                                             return c_id
                                    elif text['property'][p] == '光环':
                                        if type(mon_data[c_id][8]) == dict:
                                             return c_id 
                                    elif text['property'][p] == '受伤':
                                        if type(mon_data[c_id][10]) == dict:
                                             return c_id
                                    elif text['property'][p] == '超杀':
                                        if type(mon_data[c_id][12]) == dict:
                                             return c_id

    def all_suitable(self,owner,race,proper,position = None):
        res = []
        for i in range(len(owner.bd_mns)):
            if i != position:
                if self.suitable(owner,race,proper,i):
                    res.append(i)
        return res

    def random_suitable(self,owner,race,proper):
        target = []
        for i in range(len(owner.bd_mns)):
            if self.suitable(owner,race,proper,i):
                target.append(i)
        if len(target) != 0:
            target = random.choice(target)
            return target
        else:
            return None

    def left_suitable(self,owner,race,proper):
        for i in range(len(owner.bd_mns)):
            if self.suitable(owner,race,proper,i):
                return i
        return None

    def side_suitable(self,owner,race,proper,position):
        target = []
        for i in range(position+1,len(owner.bd_mns)):
            if self.suitable(owner,race,proper,i):
                target.append(i)
                break
        for i in range(position-1,-1,-1):
            if self.suitable(owner,race,proper,i):
                target.append(i)
                break
        return target

    def random_attack(self,owner,position,race,proper):
        target = self.random_suitable(owner.opponent,race,proper)
        if target != None:
            print(owner.bd_mns[position].name,'攻击了',owner.opponent.bd_mns[target].name)
            value0 = -owner.bd_mns[position].attk
            value1 = -owner.opponent.bd_mns[target].attk
            self.attack(position,target,value0,value1)
            return True
        else:
            #raise AttackError_NoTarget('This_no_target_to_attack.')
            return False

    #position攻击,target接受
    def attack(self,position,target,value0,value1):
        if self.opponent.bd_mns[target].proper[7] == 1:
            raise Be_AttackedError('Cannot_select_or_attack_this_mns.')
        if self.bd_mns[position].proper[7] == 1:
            raise AttackError('This_mns_Cannot_select_or_attack.')
        blood0 = self.bd_mns[position].blood_curent
        blood1 = self.opponent.bd_mns[target].blood_curent
        mns_self = self.bd_mns[position]
        opponent = self.opponent.bd_mns[target]
        posion_flag = self.bd_mns[position].proper[2]
        posion_flag1 = self.opponent.bd_mns[target].proper[2]

        self.effect(mns_self.attack_phrase,position,target)#发动效果
        
        self.bd_mns[position].damage_heal(value1,position)
        self.opponent.bd_mns[target].damage_heal(value0,target)
       
        if self.bd_mns[position].blood_curent <= 0:
            self.kill(mns_self)
        else:#剧毒
            if posion_flag1 == 1:
                if self.bd_mns[position].blood_curent < blood0:
                    self.kill(mns_self)
                    
        if opponent.blood_curent <= 0:
            self.opponent.kill(opponent)
            self.effect(mns_self.overkillean,position,target)
        else:#剧毒    
            if posion_flag == 1:
                if sopponent.blood_curent < blood1:
                    self.opponent.kill(opponent)
                    self.effect(mns_self.overkillean,position,target)
        return True
    
    def kill(self,mns):
        if type(mns) != list:
            self.kill_one(mns)
        else:
            for i in range(len(mns)):
                if not mns[i].die_flag:
                    mns[i].die()
                    self.dead_mns.append(mns[i].card_id)
            self.halo_buff_update()
            for j in range(len(mns[i].owner.bd_mns)):
                if mns[i].owner.bd_mns[j] == mns:
                    for d_r in range(self.d_r_time):#触发多次
                        self.effect(mns[i].death_rattle,j)
                    self.d_r_used.append(mns[i].card_id)
                    self.listen_phrase('die','none',mns[i])#监听死亡事件
                    if type(mns[i].death_rattle) == dict:
                        self.listen_phrase('death_rattle','none',mns[i])

    def kill_one(self,mns):
        if not mns.die_flag:
            mns.die()
            self.dead_mns.append(mns.card_id)
            self.halo_buff_update()
            for j in range(len(mns.owner.bd_mns)):
                if mns.owner.bd_mns[j] == mns:
                    for d_r in range(self.d_r_time):
                        self.effect(mns.death_rattle,j)
                    self.d_r_used.append(mns.card_id)
                    self.listen_phrase('die','none',mns)#监听死亡事件
                    if type(mns.death_rattle) == dict:
                        self.listen_phrase('death_rattle','none',mns)

    def halo_buff_set(self,owner,owner1,position,value,target):
        for i in range(len(target)):
            if target[i] == 'owner':
                pass
            else:
                if owner == owner1:
                    owner.bd_mns[target[i]].halo_buff_set(owner1.bd_mns[position],value,False)
                else:
                    owner.bd_mns[target[i]].halo_buff_set(owner1.bd_mns[position],value,True)

    def halo_immune_set(self,owner,value,target):
        for i in range(len(target)):
            if target[i] == 'owner':
                owner.hero.immune = value
            else:
                owner.bd_mns[target[i]].immune = value

    def halo_w_r_set(self,owner,value,target):
        for i in range(len(target)):
            if target[i] == 'owner':
                owner.w_r_time = value
            else:
                pass

    def halo_d_r_set(self,owner,value,target):
        for i in range(len(target)):
            if target[i] == 'owner':
                owner.d_r_time = value
            else:
                pass

    def halo_s_m_set(self,owner,value,target):
        for i in range(len(target)):
            if target[i] == 'owner':
                owner.s_m_time = value
            else:
                pass
            
    def halo_buff_update(self):
        self.halo_buff_update_owner(self)
        if type(self.opponent) != Bob:
            self.halo_buff_update_owner(self.opponent)

    def halo_buff_update_owner(self,owner):
        for i in range(len(owner.bd_mns)):
            owner.bd_mns[i].halo_buff_space[False] = {}
            owner.bd_mns[i].immune = 0
            owner.hero.immune = 0
            owner.w_r_time = 1
            owner.d_r_time = 1
            owner.s_m_time = 1
        for i in range(len(owner.opponent.bd_mns)):
            owner.opponent.bd_mns[i].halo_buff_space[True] = {}
        for i in range(len(owner.bd_mns)):
            owner.effect(owner.bd_mns[i].halo_buff,i,False)

    def show_board(self):
        print('---------------------------------------------------')
        mns = self.opponent.hero.name + '场上的随从: '
        for i in range(len(self.opponent.bd_mns)):
            proper = ''
            for j in range(len(self.opponent.bd_mns[i].proper)):
                if j != 8:
                    if self.opponent.bd_mns[i].proper[j] == 1:
                        proper += property_name[j]+' '
            mns += str(i+1)+self.opponent.bd_mns[i].name+str(int(self.opponent.bd_mns[i].attk))+'/'+str(int(self.opponent.bd_mns[i].blood_curent))+proper+' '
        print(mns)
        mns = self.hero.name + '场上的随从: '
        for i in range(len(self.bd_mns)):
            proper = ''
            for j in range(len(self.bd_mns[i].proper)):
                if j != 8:
                    if self.bd_mns[i].proper[j] == 1:
                        proper += property_name[j]+' '
            mns += str(i+1)+self.bd_mns[i].name+str(int(self.bd_mns[i].attk))+'/'+str(int(self.bd_mns[i].blood_curent))+proper+' '
        print(mns)
        print('---------------------------------------------------')

class card():
    pass
            
class Magic(card):
    def __init__(self,owner,card_id):
        self.effect = 0
        self.name = 0
        self.__listener = 0
        self.gold = 0

#随从---------------------------------------------------

class Minions(card):
    proper_begin_number_class = proper_begin_number
    def __init__(self,owner,card_id):
        self.owner = owner#拥有者
        self.card_id = card_id
        self.data = mon_data[card_id]
        self.name = self.data[0]#攻击血量等
        self.race = self.data[4]
        self.__rank = self.data[1]
        self.__attk = self.data[2]
        self.size = 0
        self.__blood = self.data[3]#血量和现有的血量
        self.__blood_curent = self.__blood
        self.__war_roar = self.data[6]#是否有战吼
        self.__death_rattle = self.data[7]
        self.__halo_buff = self.data[8]
        self.__healean = self.data[9]
        self.__hurten = self.data[10]
        self.__attack_phrase = self.data[11]
        self.__overkillean = self.data[12]
        self.__listener = self.data[13]
        self.__proper = []
        self.__halo_buff_space = {}
        self.display = 1
        self.gold = 0
        if self.name == '百变泽鲁斯':
            self.change_flag = True
        else:
            self.change_flag = False
        for i in range(self.proper_begin_number_class,self.proper_begin_number_class+len(property_name)):
            self.__proper.append(self.data[i])
        self.__die_flag = 0
        self.immune = 0

    def golden(self,mns):
        print('你获得了一个三连:',self.name)
        for i in range(len(mns)):
            self.__attk += copy.deepcopy(mns[i].attk)
            self.__blood += copy.deepcopy(mns[i].blood)
        self.__attk -= copy.deepcopy(self.data[2])
        self.__blood -= copy.deepcopy(self.data[3])
        self.__blood_curent = copy.deepcopy(self.__blood)
        self.gold = 1

        if type(self.__war_roar) == dict:
            self.__war_roar['other'].append(copy.deepcopy(self.war_roar))
        if type(self.__death_rattle) == dict:
            self.__death_rattle['other'].append(copy.deepcopy(self.data[7]))
        if type(self.__halo_buff) == dict:
            if self.__halo_buff['type'] == 'halo_death_rattle' or self.__halo_buff['type'] == 'halo_war_roar' or self.__halo_buff['type'] == 'halo_summon':
                self.__halo_buff['value'][0] = 3
            else:
                self.__halo_buff['other'].append(copy.deepcopy(self.data[8]))
        if type(self.__healean) == dict:
            self.__healean['other'].append(copy.deepcopy(self.data[9]))
        if type(self.__hurten) == dict:
            self.__hurten['other'].append(copy.deepcopy(self.data[10]))
        if type(self.__attack_phrase) == dict:
            self.__attack_phrase['other'].append(copy.deepcopy(self.data[11]))
        if type(self.__overkillean) == dict:
            self.__overkillean['other'].append(copy.deepcopy(self.data[12]))
        if type(self.__listener) == dict:
            self.__listener['other'].append(copy.deepcopy(self.data[13]))

        #给拥有者一张高星卡——————————————————————————————————
        
    def magnetic(self,mns):
        self.__attk += mns.attk
        self.__blood += mns.blood
        self.__blood_curent += mns.__blood_curent
        self.war_roar_add(mns.war_roar)
        self.death_rattle_add(mns.death_rattle)
        self.halo_buff_add(mns.halo_buff)
        self.healean_add(mns.healean)
        self.hurten_add(mns.hurten)
        self.attack_phrase_add(mns.attack_phrase)
        self.overkillean_add(mns.overkillean)
        self.listener_add(mns.listener)
        for i in range(len(mns.proper)):
            if mns.proper[i] != 0:
                if i != 5 and i != 7 and i != 8:
                    self.proper[i] = mns.proper[i]  
    @property
    def rank(self):
        return self.__rank

    @rank.setter
    def rank(self,value):
        self.__rank = value

    @property
    def attk(self):
        attk_tempt = self.__attk
        for i in self.halo_buff_space:
            for j in self.halo_buff_space[i]:
                attk_tempt += self.halo_buff_space[i][j][0]
        return attk_tempt
    
    @attk.setter
    def attk(self,value):
        self.__attk = value

    @property
    def proper(self):
        return self.__proper

    @proper.setter
    def proper(self,value):
        self.__proper = value

    def proper_name(self,name):
        for i in range(len(self.proper)):
            if len(name) == 3:
                if property_name[i] == name[1:]:
                    return not self.proper[i]
            else:
                if property_name[i] == name:
                    return self.proper[i]

    def proper_value(self,value):
        return self.proper[value]
   
    @property
    def blood(self):
        blood_tempt = self.__blood
        for i in self.halo_buff_space:
            for j in self.halo_buff_space[i]:
                blood_tempt += self.halo_buff_space[i][j][1]
        return blood_tempt
            
    @blood.setter
    def blood(self, value):
        self.__blood = value
        if self.blood_curent>self.__blood:
            self.blood_curent = self.__blood

    @property
    def blood_curent(self):
        blood_tempt = self.__blood_curent
        for i in self.halo_buff_space:
            for j in self.halo_buff_space[i]:
                blood_tempt += self.halo_buff_space[i][j][1]
        return blood_tempt
            
    @blood_curent.setter
    def blood_curent(self,value):
        self.__blood_curent = value
        if self.__blood_curent>self.__blood:
            self.__blood_curent = self.__blood

    #--------------------------------------------------
    
    @property
    def war_roar(self):
        return self.__war_roar

    def war_roar_add(self,text):
        if type(text) == dict:
            if type(self.__war_roar) == dict:
                self.__war_roar['other'].append(text)
            else:
                self.__war_roar = text

    @property
    def war_roar_manual(self):
        pass

    @property
    def death_rattle(self):
        return self.__death_rattle

    def death_rattle_add(self,text):
        if type(text) == dict:
            if type(self.__death_rattle) == dict:
                self.__death_rattle['other'].append(text)
            else:
                self.__death_rattle = text
    
    @property
    def hurten(self):
        return self.__hurten

    def hurten_add(self,text):
        if type(text) == dict:
            if type(self.__hurten) == dict:
                self.__hurten['other'].append(text)
            else:
                self.__hurten = text

    @property
    def healean(self):
        return self.__healean

    def healean_add(self,text):
        if type(text) == dict:
            if type(self.__healean) == dict:
                self.__healean['other'].append(text)
            else:
                self.__healean = text

    @property
    def halo_buff_space(self):
        return self.__halo_buff_space

    @halo_buff_space.setter
    def halo_buff_space(self,value):
        self.__halo_buff_space = value
    
    @property
    def halo_buff(self):
        return self.__halo_buff

    def halo_buff_add(self,text):
        if type(text) == dict:
            if type(self.__halo_buff) == dict:
                self.__halo_buff['other'].append(text)
            else:
                self.__halo_buff = text

    @property
    def attack_phrase(self):
        return self.__attack_phrase

    def attack_phrase_add(self,text):
        if type(text) == dict:
            if type(self.__attack_phrase) == dict:
                self.__attack_phrase['other'].append(text)
            else:
                self.__attack_phrase = text

    @property
    def overkillean(self):
        return self.__overkillean

    def overkillean_add(self,text):
        if type(text) == dict:
            if type(self.__overkillean) == dict:
                self.__overkillean['other'].append(text)
            else:
                self.__overkillean = text
                
    @property
    def listener(self):
        return self.__listener

    def listener_add(self,text):
        if type(text) == dict:
            if type(self.__listener) == dict:
                self.__listener['other'].append(text)
            else:
                self.__listener = text

    #---------------------------------------------------

    #所有伤害统一入口
    def damage_heal(self,value,position):
        if value < 0:
            if self.immune != 1:
                if self.proper[0] == 1:
                    self.shield_lose(position)
                else:
                    self.blood_curent += value
                    self.hurt(position)
            else:
                print(self.name,'免疫了伤害')  
        elif value > 0:
            self.blood_curent += value
            self.heal(position)

    #所有buff统一入口
    def buff(self,attk,blood):
        self.__attk += attk
        self.__blood += blood
        self.__blood_curent += blood

    #所有halo统一入口
    def halo_buff_set(self,mns,value,opponent = False):
        self.__halo_buff_space[opponent] = {mns:value}
        if self.blood_curent <= 0:
            self.blood_curent += (1 - self.blood_curent)

    #统一属性设置入口
    def set_proper_name(self,name,value):
        for i in range(len(self.proper)):
            if property_name[i] == name:
                return self.set_proper(i,value)

    def set_proper(self,value,value1):
        self.proper[value] = value1
        return True

    def die(self):
        if self.proper[4] == 1:
            print(self.name,'死亡但是复生了')
            self.Reborn(self.position_self())
        else:
            print(self.name,'死亡了...')
            self.set_proper(8,0)
            self.set_proper(7,1)
            self.display = 0
            self.__die_flag = 1

    @property
    def die_flag(self):
        return self.__die_flag

    def disappear(self):
        pass

    def position_self(self):
        for i in range(len(self.owner.bd_mns)):
            if self.owner.bd_mns[i] == self:
                return i

    def shield_lose(self,position):
        self.set_proper(0,0)
        self.owner.listen_phrase('shield_lose',position,self)

    def Reborn(self,position = None):
        if position == None:
            position = self.position_self()
        self.card_recover(position)
        self.set_proper(4,0)
        self.owner.listen_phrase('Reborn',position,self)
        
    def hurt(self,position):
        self.owner.effect(self.hurten,position)

    def heal(self,position):
        self.owner.effect(self.healean,position)

    def zerus(self,card_id):
        if self.change_flag:
            self.change_card(card_id)
            print(mon_data[self.card_id][0],'变成了',self.name)

    #恢复卡的本来样子
    def card_recover(self,position):
        self.data = mon_data[self.card_id]
        self.name = self.data[0]#攻击血量等
        self.race = self.data[4]
        self.__rank = self.data[1]
        self.__attk = self.data[2]
        self.__blood = self.data[3]#血量和现有的血量
        self.__blood_curent = self.__blood
        self.__war_roar = self.data[6]#是否有战吼
        self.__death_rattle = self.data[7]
        self.__halo_buff = self.data[8]
        self.__healean = self.data[9]
        self.__hurten = self.data[10]
        self.__attack_phrase = self.data[11]
        self.__overkillean = self.data[12]
        self.__listener = self.data[13]
        self.__proper = []
        self.__halo_buff_space = {}
        for i in range(self.proper_begin_number_class,self.proper_begin_number_class+len(property_name)):
            self.__proper.append(self.data[i])
        self.__die_flag = 0

    def change_card(self,card_id):
        self.data = mon_data[card_id]
        self.name = self.data[0]#攻击血量等
        self.race = self.data[4]
        self.__rank = self.data[1]
        self.__attk = self.data[2]
        self.__blood = self.data[3]#血量和现有的血量
        self.__blood_curent = self.__blood
        self.__war_roar = self.data[6]#是否有战吼
        self.__death_rattle = self.data[7]
        self.__halo_buff = self.data[8]
        self.__healean = self.data[9]
        self.__hurten = self.data[10]
        self.__attack_phrase = self.data[11]
        self.__overkillean = self.data[12]
        self.__listener = self.data[13]
        self.__proper = []
        self.__halo_buff_space = {}
        for i in range(self.proper_begin_number_class,self.proper_begin_number_class+len(property_name)):
            self.__proper.append(self.data[i])

class Hero(Minions):
    proper_begin_number_class = Minions.proper_begin_number_class
    def __init__(self,owner,hero_id):
        self.owner = owner#拥有者
        self.hero_id = hero_id
        self.data = hero_data[hero_id]
        #攻击血量等
        self.name = self.data[0]
        self.race = '-'
        self.__rank = 1
        self.__attk = 0
        self.size = 0
        self.instance = True
        #血量和现有的血量
        self.__blood = self.data[1]
        self.__blood_curent = self.__blood
        self.__rank_fee = (5,7,8,9,11,0)
        self.__rank_fee_curent = 5
        self.__die_flag = 0
        #等级
        self.__rank = 1
        self.__war_roar = 0#是否有战吼
        self.__death_rattle = 0
        self.__halo_buff = 0
        self.__healean = 0
        self.__hurten = 0
        self.__proper = []
        for i in range(self.proper_begin_number_class,self.proper_begin_number_class+len(property_name)):
            self.__proper.append(0)
        self.immune = False

    def hurt(self,position):
        self.owner.listen_phrase('hero_hurt',position,self)

    @property
    def proper(self):
        return self.__proper
        

    #等级花费
    @property
    def rank_fee(self):
        return self.__rank_fee[self.rank-1]

    #具体的等级费用
    @property
    def rank_fee_curent(self):
        return self.__rank_fee_curent

    @rank_fee_curent.setter
    def rank_fee_curent(self,value):
        self.__rank_fee_curent = value
        if self.__rank_fee_curent<=0:
            self.__rank_fee_curent=0
    
    #等级
    @property
    def rank(self):
        return self.__rank

    @rank.setter
    def rank(self,value):
        self.__rank = value
        if self.__rank<=0:
            self.__rank = 1
        elif self.__rank>6:
            self.__rank = 6
            
    def up_rank(self):
        self.rank += 1

    @property
    def blood(self):
        return self.__blood
            
    @blood.setter
    def blood(self, value):
        self.__blood = value
        if self.blood_curent>self.__blood:
            self.blood_curent = self.__blood

    @property
    def blood_curent(self):
        return self.__blood_curent
            
    @blood_curent.setter
    def blood_curent(self, value):
        self.__blood_curent = value
        if self.__blood_curent>self.__blood:
            self.__blood_curent = self.__blood

    def die(self):
        self.proper[8] = 0
        self.proper[7] = 1
        self.__die_flag = 1
        pass

    @property
    def die_flag(self):
        return self.__die_flag

    @property
    def war_roar(self):
        return self.__war_roar

    @property
    def war_roar_manual(self):
        pass

    @property
    def death_rattle(self):
        return self.__death_rattle
    
    @property
    def hurten(self):
        return self.__hurten

    @property
    def healean(self):
        return self.__healean
    
    @property
    def halo_buff(self):
        return self.__halo_buff
