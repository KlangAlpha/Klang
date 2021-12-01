import pandas as pd
from Klang import Kl,Klang_init,C
from Klang import SequenceTransformer


#归化数据
def scaler_data(x):
    ret = x/x.values[-1] 
    return ret

 
df = Kl.data_engine.get_day("五矿稀土",'sz.000831','2021-01-01','2021-12-01')



def get_feature(df1,target,code):

    st_close = SequenceTransformer(addcalc=[
    {'name':'ma','fname':'ma10','param':10},
    {'name':'ma','fname':'ma20','param':20},
    {'name':'ma','fname':'ma30','param':30},
    ])

    retclose =  st_close.transform(scaler_data(df1['close']))


    st_vol = SequenceTransformer(calculators=[
        {'name':'rise','fname':'rise','param':-2},
        ],addcalc=[
        {'name':'ma','fname':'ma20','param':20},
    ])
    retvol = st_vol.transform(scaler_data(df1['vol']))

    retclose.update(retvol)
    retclose.update(target)
    retclose.update({'code':code,'datetime':df1['datetime'].values[-1]})

    return retclose
    #df1['date'].values[-1])

all_list = []
def get_features(df,code):
    
    for i in range(60,len(df)-10):

        m = max(df['close'].values[i+1:i+10]) / df['close'].values[i]
        if m > 1.1:
            target = 1
        else :
            target = 0 
        ret = get_feature(df.iloc[:i,],{'target':target},code)
        all_list.append(ret)

    print(all_list[-1])

Klang_init()

for df in Kl.df_all:
    try:
        Kl.code(df['code'])
        print("****",df['code'],df['name'],C,"****")
        #df2 = Kl.data_engine.get_day(df['name'],df['code'],'2021-01-01','2021-12-01')
        get_features(df['df'],df['code'])
    except KeyboardInterrupt:
        break
    except :
        pass
