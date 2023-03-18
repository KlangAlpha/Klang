
import sys
from pathlib import Path # if you haven't already done so
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))

import pandas as pd
from Klang import Kl,Klang_init,C
from Klang import SequenceTransformer


#归化数据
def scaler_data(x):
    ret = x/x.values[-1] 
    return ret

 
#df = Kl.data_engine.get_day("五矿稀土",'sz.000831','2021-01-01','2021-12-01')
fields = [
       {'name':'fist_location_of_max'}, #第一次最大值出现的位置
       {'name':'fist_location_of_min'}, #第一次最小值出现的位置
       {'name':'ndex_mass_quantile_50'},
       {'name':'ndex_mass_quantile_75'},
       {'name':'_ndex_mass_quantile_25'},
       {'name':'kurtosis'}, #峰度
       {'name':'last_location_of_max'}, #最后一次最大值出现的位置
       {'name':'last_location_of_min'}, #做后一次最小值出现的位置
       {'name':'ma'}, # ma，默认是5 
       {'name':'macd'}, # macd，返回macd值
       {'name':'max'},  #周期内最大值
       {'name':'mean'}, # 周期内平均值
       {'name':'min_change'}, 
       {'name':'min'}, #最小值
       {'name':'none_rate'},
       {'name':'number_peaks_1'}, #峰值数
       {'name':'number_peaks_2'}, 
       {'name':'number_peaks_3'},
       {'name':'percentage_below_mean'}, #<平均值的占比
       {'name':'ratio_value_number_to_seq_length'},#相同项目占比 
       {'name':'skewness'},#斜率 ，偏度
       {'name':'standard_deviation'}, #标准方差 
       {'name':'variance'}, #方差 
       ]
       #'rise', #涨幅,一般是与前一日相比
       #'freq_of_max', #最大值出现的次数 
       #'freq_of_min', #最小值出现的次数
       #'length',  #总长度
       #'duplicates_count', #相同值的个数
       #'uniqueCount', #不同值的个数
       #'ma10', 'ma20', 'ma30', # 股票MA 计算通过参数获取不同的值
       #'median', #周期内中间位置的值，和平均值是不同的，这个是值周期的中间
       #'median_mean_distance', # 平均值和周期中间的差值距离
       #'percentage_of_most_reoccuring_value_to_all_values', #
       #'percentage_of_most_reoocuring_value_to_all_datapoints', #





def get_feature(df1,target,code):

    st_close = SequenceTransformer(calculators=fields,addcalc=[
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
        df_ret = pd.DataFrame(all_list)
        df_ret.to_csv("~/.test_feat.csv")
        break
    except :
        pass
    
df_ret = pd.DataFrame(all_list)
df_ret.to_csv("~/.test_feat.csv")
