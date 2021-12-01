import pandas as pd
from Klang import Kl
from Klang import SequenceTransformer


#归化数据
def scaler_data(x):
    ret = x/x.values[-1] 
    return ret

 
df = Kl.data_engine.get_day("五矿稀土",'sz.000831','2021-01-01','2021-12-01')



def get_feature(df1,target):

    st_close = SequenceTransformer(addcalc=[
    {'name':'ma','fname':'ma10','param':10},
    {'name':'ma','fname':'ma20','param':20},
    {'name':'ma','fname':'ma30','param':30},
    ])

    print(st_close.transform(scaler_data(df1['close'])))


    st_vol = SequenceTransformer(calculators=[
        {'name':'rise','fname':'rise','param':-2},
        ],addcalc=[
        {'name':'ma','fname':'ma20','param':20},
    ])
    print(st_vol.transform(scaler_data(df1['vol'])))

    print(target)
    #df1['date'].values[-1])

for i in range(60,len(df)-10):

    m = max(df['close'].values[i+1:i+10]) / df['close'].values[i]
    if m > 1.1:
        target = 1
    else :
        target = 0 
    get_feature(df.iloc[:i,],{'target':target})

