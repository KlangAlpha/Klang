#
# klang.org.cn 提供的股票数据
# 数据来自baostock + tdx
# 为了加速Klang运行，数据会被存到本地文件
# 并且加载到内存
#

import pandas as pd
import os
import json
from threading import Lock
import requests
import time

filename_sl = os.path.expanduser("~/.klang_stock_list.csv")
filename_st = os.path.expanduser("~/.klang_stock_trader.csv")

hostname="http://klang.org.cn"
hostname="http://klang.zhanluejia.net.cn"
mutex = Lock()

#
#stock list
#
def updatestocklist(stname=filename_sl):

    json = requests.get(hostname+"/industries").json()
    df = pd.json_normalize(json)
    df = df.drop(columns=['_id','updatedAt','id','createdAt'])
    # 结果集输出到csv文件
    df.to_csv(stname, index=False,columns=['updateDate','code','code_name','industry','industryClassification','tdxbk','tdxgn'])    

def updatestockdata(Kl):

    stocklist = Kl.stocklist
    df_dict = []
    for stock in stocklist:
        code ,name ,tdxbk,tdxgn= getstockinfo(stock)
        #print('正在获取',name,'代码',code)
        df = get_day(name,code,Kl.start_date,Kl.end_date)
        if len(df) > 0:
            df_dict.append({'df':df.to_dict(),'name':name,'code':code,'tdxbk':tdxbk,'tdxgn':tdxgn})
        else:
            df_dict.append({'df':{},'name':name,'code':code,'tdxbk':tdxbk,'tdxgn':tdxgn})

    save_stock_trader(df_dict)
    load_stock_trader(Kl)


def init_stock_list(Kl,offset=0):
    if not os.path.exists(filename_sl):
        print('正在下载股票库列表....')
        updatestocklist(filename_sl)
        print("股票列表下载完成")

    print("正在从文件",filename_sl,"加载股票列表")
    stocklist = open(filename_sl).readlines()
    stocklist = stocklist[1+int(offset):] #删除第一行

    # 初始化 code到index 对应表
    number = 0
    Kl.df_all = []
    for stock in stocklist:
            code ,name ,tdxbk,tdxgn = getstockinfo(stock)
            Kl.stockindex[code] = number
            Kl.df_all.append({"name":name,"df":None,"code":code,"tdxbk":tdxbk,"tdxgn":tdxgn}) 
            number += 1
        

    return stocklist

#
# all stock trader day K data
#
def save_stock_trader(df_dict):
    content = json.dumps(df_dict)    
    f = open(filename_st,"w+")
    f.write(content)
    f.close()

# load stock data from file
def load_stock_trader(Kl,name=filename_st):
    content = open(name).read()

    df_dict = json.loads(content)
    number = 0
    for stock in df_dict:
            # save order for index
            #code = stock['code']
            #name = stock['name']
            # save df to list
            df = pd.DataFrame.from_dict(stock['df'])
            if len(df) > 2:
                df['datetime'] = df['date']
                df = df.set_index('date')
            Kl.df_all[number]["df"] = df
            number += 1


#从bs获取日K数据
def get_day(name,code,start,end,setindex=False):
    mutex.acquire()
    try:
        json = requests.get(hostname+"/dayks",
            params={"code":code,"end":end,"limit":200},timeout=1000).json()
    except:
        time.sleep(2)
        json = requests.get(hostname+"/dayks",
            params={"code":code,"end":end,"limit":200},timeout=1000).json()
   
    #df = pd.io.json.json_normalize(json)
    df = pd.json_normalize(json)
    if len(df) < 1:
       mutex.release()
       return []
    df = df.drop(columns=['_id','codedate','id'])
    datas = df.sort_values(by="date",ascending=True)



    mutex.release()

    #print(len(datas),datas.date[datas.index[-1]])
    if setindex == True:
        datas['datetime'] = datas['date']
        datas = datas.set_index('date')
    close  = datas['close'].iloc[-1]
    volume = datas['volume'].iloc[-1]
    turn   = datas['turn'].iloc[-1]
    try :
        datas['hqltsz'] = float(volume) * float(close)/ float(turn) / 1000000 
    except:
        datas['hqltsz'] = 0.0001 #没有交易量
    datas.rename(columns={'volume':'vol'},inplace = True) 

    return datas

# 从文件中一行数据 格式化分析出信息
# 2019-12-09,sz.002094,青岛金王,化工,申万一级行业
# 时间，股票代码，名称，类别
def getstockinfo(stock):
    stock = stock.strip()
    d,code,name,skip1,skip2,tdxbk,tdxgn = stock.split(',')
    return code,name,tdxbk,tdxgn


#
# 从网上下载数据或者从文件加载股票数据    
# 加载后数据存放在(Kl.df_all)
#
def get_all_day(Kl):
    stocklist = Kl.stocklist
    df_dict = []
    # 如果文件存在,可以直接从文件加载数据
    # 要强制从网上加载数据,可以设置reload=True
    if os.path.exists(filename_st) and not Kl.reload:
        print("正在从文件",filename_st,"加载数据")
        load_stock_trader(Kl)
        return 

    print("正在从网上下载股票数据,时间将会有点长")
    for stock in stocklist:
        code ,name,tdxbk,tdxgn = getstockinfo(stock)
        #print('正在获取',name,'代码',code)
        df = get_day(name,code,Kl.start_date,Kl.end_date)
        if len(df) > 0:
            df_dict.append({'df':df.to_dict(),'name':name,'code':code,'tdxbk':tdxbk,'tdxgn':tdxgn})
        else:
            df_dict.append({'df':{},'name':name,'code':code,'tdxbk':tdxbk,'tdxgn':tdxgn})
                
    save_stock_trader(df_dict)
    load_stock_trader(Kl)
