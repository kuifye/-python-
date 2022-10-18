from Minions import *


class Game:
    def __init__(self,mon_data):
        self.bob = Bob()
        self.bob.begin(mon_data)
        self.p = []
        for i in range(11):
            p_this = Player(i)
            p_this.game=self
            self.p.append(p_this)
            p_this.refresh_free()
            
        a4 = Minions(self.p[0],40)
        a5 = Minions(self.p[0],40)
        a6 = Minions(self.p[0],104)
        a9 = Minions(self.p[0],87)
        a10 = Minions(self.p[0],39)
        a11 = Minions(self.p[0],39)
        a12 = Minions(self.p[0],39)
        a13 = Minions(self.p[0],96)
        a14 = Minions(self.p[0],39)
        a15 = Minions(self.p[0],100)
        a16 = Minions(self.p[0],100)

        self.p[0].bd_mns.append(a4)
        self.p[0].bd_mns.append(a5)
        self.p[0].bd_mns.append(a6)
        self.p[0].bd_mns.append(a9)
        self.p[0].cd_mns.append(a10)
        self.p[0].cd_mns.append(a11)
        self.p[0].cd_mns.append(a12)
        self.p[0].cd_mns.append(a13)
        self.p[0].cd_mns.append(a14)
        self.p[0].cd_mns.append(a15)
        self.p[0].cd_mns.append(a16)
        
        self.p[0].halo_buff_update()

        a7 = Minions(self.p[1],101)
        a8 = Minions(self.p[1],105)
        a3 = Minions(self.p[1],105)
        a1 = Minions(self.p[1],40)
        a2 = Minions(self.p[1],54)
        self.p[1].bd_mns.append(a7)
        self.p[1].bd_mns.append(a8)
        self.p[1].bd_mns.append(a3)
        self.p[1].bd_mns.append(a1)
        self.p[1].bd_mns.append(a2)
        
        self.show_game(0)                   
        self.console(0)
        
#----------------------------------------------
        
    def next_turn_p(self,p):
        print('-----------------------------------------------------------------')
        print('')
        self.battle(p,1)

    def battle(self,p,p1):
        
        self.p[p].turn_over()
        self.p[p1].turn_over()
        
        board = copy.deepcopy(self.p[p].bd_mns)
        dead_mns = copy.deepcopy(self.p[p].dead_mns)
        w_roar_used = copy.deepcopy(self.p[p].w_roar_used)
        d_r_used = copy.deepcopy(self.p[p].d_r_used)
        
        board1 = copy.deepcopy(self.p[p1].bd_mns)
        dead_mns1 = copy.deepcopy(self.p[p1].dead_mns)
        w_roar_used1 = copy.deepcopy(self.p[p1].w_roar_used)
        d_r_used1 = copy.deepcopy(self.p[p1].d_r_used)
        
        self.p[p].last_opponent = copy.deepcopy(self.p[p1].bd_mns)
        self.p[p1].last_opponent = copy.deepcopy(self.p[p].bd_mns)
        
        self.show_board(p)
        self.show_board(p1)
        self.print_line()
        
        #放置作战指示器
        attack_mns0 = Minions(self.p[p],15)
        self.p[p].pull_in(self.p[p],attack_mns0,0)
        attack_mns1 = Minions(self.p[p1],15)
        self.p[p1].pull_in(self.p[p1],attack_mns1,0)
        #准备开战
        self.p[p].opponent = self.p[p1]
        self.p[p1].opponent = self.p[p]
        self.p[p].battle_begin()
        self.p[p1].battle_begin()
        
        self.show_board(p)
        self.show_board(p1)
        self.print_line()
        
        #开战
        first_attk_flag = 0
        if self.p[p1].size() > self.p[p].size():
            first_attk_flag = 1
        elif self.p[p].size() > self.p[p1].size():
            first_attk_flag = 0
        else:
            first_attk_flag =  random.randrange(0,2,1)
            
        while True:
            if self.against_over(p,p1):
                break
            if first_attk_flag == 0:
                first_attk_flag = 1
                target = self.attak_mns(p)
                mns_this = self.p[p].bd_mns[target]
                
                if not self.p[p].random_attack(self.p[p],target,'-',['嘲讽']):
                    self.p[p].random_attack(self.p[p],target,'-',['-'])
                #如果右边的怪死了就往后一个位置
                if not mns_this.die_flag:
                    target = self.attak_mns_self(p)
                    self.p[p].next_position(target)
            else:
                first_attk_flag = 0
                target = self.attak_mns(p1)
                mns_this = self.p[p1].bd_mns[target]

                if not self.p[p1].random_attack(self.p[p1],target,'-',['嘲讽']):
                    self.p[p1].random_attack(self.p[p1],target,'-',['-'])

                if not mns_this.die_flag:
                    target = self.attak_mns_self(p1)
                    self.p[p1].next_position(target)
            

            self.print_line()
            self.show_board(p)
            self.show_board(1)
            
        #结算
        self.p[p].battle_over()
        self.p[p1].battle_over()
        
        self.p[p].opponent = self.bob
        self.p[1].opponent = self.bob
        self.p[p].bd_mns = board
        self.p[p].dead_mns = dead_mns
        self.p[p].w_roar_used = w_roar_used
        self.p[p].d_r_used = d_r_used
        
        self.p[p1].bd_mns = board1
        self.p[p1].dead_mns = dead_mns1
        self.p[p1].w_roar_used = w_roar_used1
        self.p[p1].d_r_used = d_r_used1

        self.p[p].next_turn()
        self.p[p].get_refresh_amount()
        self.p[p1].next_turn()
        self.p[p1].get_refresh_amount()
        
    def attak_mns(self,p):
        len_bd = len(self.p[p].bd_mns)
        for i in range(len_bd):
            if self.p[p].bd_mns[i].name == '攻击标记':
                if i+1 >= len_bd:
                    target = 0
                else:
                    target = i+1
                while True:
                    if target >= len_bd:
                        target = 0
                    if self.p[p].bd_mns[target].proper_value(7)!=1:
                        break
                    else:
                        target+=1
                return target
                
    def attak_mns_self(self,p):
        len_bd = len(self.p[p].bd_mns)
        for i in range(len_bd):
            if self.p[p].bd_mns[i].name == '攻击标记':
                return i

  
    def against_over(self,p,p1):
        if self.p[p].size() <=0 and self.p[p1].size()<=0:
            self.print_line()
            print('平局...')
            print('战斗结束')
            self.print_line()
            return True
        elif self.p[p1].size() <= 0:
            damage = self.p[p].hero.rank
            for i in range(len(self.p[p].bd_mns)):
                if self.p[p].bd_mns[i].rank == 0 and self.p[p].bd_mns[i].name != '攻击标记' and self.p[p].bd_mns[i].proper[7] != 1:
                    damage += 1
                elif self.p[p].bd_mns[i].rank == None:
                    pass
                elif self.p[p].bd_mns[i].proper[7] != 1:
                    damage += self.p[p].bd_mns[i].rank
            self.p[p1].hero.damage_heal(-damage,'owner')
            self.print_line()
            
            self.p[p].win_flag = True
            self.p[p1].win_flag = False
            print(self.p[p].hero.name,'胜出!   ',self.p[p1].hero.name,'少了',damage,'点血')
            print('战斗结束')
            self.print_line()
            return True
        elif self.p[p].size() <= 0:
            damage = self.p[p1].hero.rank
            for i in range(len(self.p[p1].bd_mns)):
                if self.p[p1].bd_mns[i].rank == 0 and self.p[p1].bd_mns[i].name != '攻击标记' and self.p[p1].bd_mns[i].proper[7] != 1:
                    damage += 1
                elif self.p[p1].bd_mns[i].rank == None:
                    pass
                elif self.p[p1].bd_mns[i].proper[7] != 1:
                    damage += self.p[p1].bd_mns[i].rank
            self.p[p].hero.damage_heal(-damage,'owner')
            self.print_line()
            
            self.p[p1].win_flag = True
            self.p[p].win_flag = False
            print(self.p[p1].hero.name,'胜出...   ',self.p[p].hero.name,'少了',damage,'点血')
            print('战斗结束')
            self.print_line()
            return True
        else:
            return False

    def print_line(self):
        print('')
        print('---------------------------------------------------------------------------')
        print('')

#----------------------------------------------

    def show_cell(self,p):
        mns = '鲍勃出售的随从: '
        for i in range(len(self.p[p].store_mns)):
            mns += str(i+1)+self.p[p].store_mns[i].name+' '
        print(mns)

    def show_state(self,p):
        print('剩余的费用: ',self.p[p].fee,' 升级费用:',self.p[p].rank_fee_curent,' 等级:',self.p[p].hero.rank,' 血量:',self.p[p].hero.blood_curent)
    
    def show_hand(self,p):
        if self.p[p].card_len() > 0:
            mns = '你手里的随从: '
            for i in range(len(self.p[p].cd_mns)):
                mns += str(i+1)+self.p[p].cd_mns[i].name
                if self.p[p].cd_mns[i].gold == 1:
                    mns += ' 金色'
                mns += ' '
            print(mns)
            return True
        else:
            print('你没有手牌...')
            return False

    def show_board(self,p):
        mns = self.p[p].hero.name + '场上的随从: '
        for i in range(len(self.p[p].bd_mns)):
            if self.p[p].bd_mns[i].proper[7] == 0 and self.p[p].bd_mns[i].proper[8] != 0:
                proper = ''
                for j in range(len(self.p[p].bd_mns[i].proper)):
                    if j != 8:
                        if self.p[p].bd_mns[i].proper[j] == 1:
                            proper += property_name[j]+' '
                mns += str(i+1)+self.p[p].bd_mns[i].name+str(int(self.p[p].bd_mns[i].attk))+'/'+str(int(self.p[p].bd_mns[i].blood_curent))+proper+' '
        print(mns)

    def show_game(self,p):
        self.show_cell(p)
        self.show_state(p)
        self.show_board(p)
        self.show_hand(p)

    def console(self,p):
        print('')
        flag = input('刷新r/购买b/手牌h/场面d/升级u/退出q/冻结f/下一回合n:')
        if flag == 'b':
            self.show_cell(p)
            flag = input('买第几个：')
            self.p[p].buy(int(flag)-1)
            self.show_cell(p)
            self.show_hand(p)
        elif flag == 'r':
            if self.p[p].refresh():
                self.show_cell(p)
        elif flag == 'h':
            if self.show_hand(p):
                flag = input('q返回/输入数字召唤对应随从：')
                if flag != 'q':
                    flag = int(flag)-1
                    if self.p[p].size() == 0:
                        position = 0
                    else:
                        self.show_board(p)
                        position = int(input('召唤到哪个位置上：'))-1
                        if position <0:
                            position = 0
                        elif position >= len(self.p[p].bd_mns):
                            position = len(self.p[p].bd_mns)
                    if self.p[p].munual(flag):
                        if self.p[p].size() == 0:
                            self.p[p].use(flag,position)
                        else:
                            self.show_board(p)
                            target = int(input('你想对谁使用战吼：'))-1
                            self.p[p].use(flag,position,target)
                    else:
                        self.p[p].use(flag,position)
                self.show_board(p)
                    
        elif flag == 'd':
            self.show_board(p)
            flag = input('返回q/想要卖出第几个：')
            if flag != 'q':
                if self.p[p].cell(int(flag)-1):
                    self.show_board(p)
                    self.show_state(p)
                else:
                    print('卖出失败了...')
        elif flag == 'n':
            self.next_turn_p(0)
            self.show_game(p)
        elif flag == 'f':
            if self.p[p].freezen():
                print('成功冻结！')
            else:
                print('成功解冻！')
        elif flag == 'u':
            if self.p[p].up_rank():
                print('成功升级！')
            else:
                print('升级失败...')
            self.show_state(p)
        elif flag == 'q':
            return True
        self.console(p)


if __name__ == "__main__":
    p = Player(0)
    c = Minions(p,26)
    G = Game(mon_data)
