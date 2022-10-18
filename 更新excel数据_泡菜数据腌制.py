import xlrd
import xlwt
import pickle

def dump():
    #腌制随从列表
    data = xlrd.open_workbook('dateMonester.xlsx')
    table = data.sheets()[0]
    mon_data = []
    for i in range(1,len(table.col_values(0))):
        mon_data.append(table.row_values(i))

    #函数
    for k in range(6,14):
        for i in range(1,len(mon_data)):
            if mon_data[0][k] != '0':
                try:
                    mon_data[i][k] = eval(mon_data[i][k])
                except:
                    mon_data[i][k] = 0
            else:
                mon_data[i][k] = 0

        #等级攻击血量
        for j in range(1,4):
            mon_data[i][j] = int(float(mon_data[i][j]))

        #属性
        for j in range(14,23):
            mon_data[i][j] = int(float(mon_data[i][j]))

    
    pickle_file = open('mon_data.pkl','wb')
    pickle.dump(mon_data,pickle_file)
    pickle_file.close()

    #腌制等级序数表
    Rank_mns = [0,0,0,0,0,0,0]
    for i in range(len(mon_data)):
        if mon_data[i][1]==0:
            Rank_mns[0]+=1
        elif mon_data[i][1]==1:
            Rank_mns[1]+=1
        elif mon_data[i][1]==2:
            Rank_mns[2]+=1
        elif mon_data[i][1]==3:
            Rank_mns[3]+=1
        elif mon_data[i][1]==4:
            Rank_mns[4]+=1
        elif mon_data[i][1]==5:
            Rank_mns[5]+=1
        elif mon_data[i][1]==6:
            Rank_mns[6]+=1
    Rank_mns[1]+= Rank_mns[0]
    Rank_mns[2]+= Rank_mns[1]
    Rank_mns[3]+= Rank_mns[2]
    Rank_mns[4]+= Rank_mns[3]
    Rank_mns[5]+= Rank_mns[4]
    Rank_mns[6]+= Rank_mns[5]
    print(Rank_mns)

    pickle_file2 = open('Rank_mns.pkl','wb')
    pickle.dump(Rank_mns,pickle_file2)
    pickle_file2.close()

    return mon_data

if __name__ == "__main__":
    #腌制随从列表
    data = xlrd.open_workbook('dateMonester.xlsx')
    table = data.sheets()[0]
    mon_data = []
    for i in range(1,len(table.col_values(0))):
        mon_data.append(table.row_values(i))
    a = dump()
    b = mon_data
        
    

    
