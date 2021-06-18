import baostock as bs
import pandas as pd
import os
import json
from threading import Lock
bs.login()


filename_sl = os.path.expanduser("~/.klang_stock_list.csv")
filename_st = os.path.expanduser("~/.klang_stock_trader.csv")


mutex = Lock()

#
#stock list
#
def updatestocklist(stname=filename_sl):
    rs = bs.query_stock_industry()

    # 打印结果集
    industry_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        row = rs.get_row_data()
        kdata = bs.query_history_k_data_plus(row[1], 
                                      'date,open,high,low,close,volume', 
                                      start_date='2021-05-20',
                                      frequency='d')
        stockd =kdata.get_data()
        if len(stockd) < 3:
            continue
        print(row)
        industry_list.append(row)
    result = pd.DataFrame(industry_list, columns=rs.fields)
    # 结果集输出到csv文件
    result.to_csv(stname, index=False)    

def updatestockdata(Kl):
    stocklist = Kl.stocklist
    df_dict = []
    for stock in stocklist:
        code ,name = getstockinfo(stock)
        #print('正在获取',name,'代码',code)
        df = get_day(name,code,Kl.start_date,Kl.end_date)
        if len(df) > 0:
           df_dict.append({'df':df.to_dict(),'name':name,'code':code})

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
            code ,name = getstockinfo(stock)
            Kl.stockindex[code] = number
            Kl.df_all.append({"name":name,"df":None,"code":code}) 
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
            code = stock['code']
            name = stock['name']
            # save df to list
            df = pd.DataFrame.from_dict(stock['df'])
            df['datetime'] = df['date']
            df = df.set_index('date')
            Kl.df_all[number]["df"] = df
            number += 1


#从bs获取日K数据
def get_day(name,code,start,end,setindex=False):
    mutex.acquire()
    rs = bs.query_history_k_data_plus(code, 
                                      'date,open,high,low,close,volume,code,turn,amount', 
                                      start_date=start,
                                      end_date=end,frequency='d' )
    datas = rs.get_data()
    mutex.release()

    if len(datas) < 2:
        return []
    #print(len(datas),datas.date[datas.index[-1]])
    if setindex == True:
        datas['datetime'] = datas['date']
        datas = datas.set_index('date')

    datas.rename(columns={'volume':'vol'},inplace = True) 

    return datas

# 从文件中一行数据 格式化分析出信息
# 2019-12-09,sz.002094,青岛金王,化工,申万一级行业
# 时间，股票代码，名称，类别
def getstockinfo(stock):
    d,code,name,skip1,skip2 = stock.split(',')
    return code,name


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

    print("正在从网上下载股票数据,时间回有点长")
    for stock in stocklist:
        code ,name = getstockinfo(stock)
        #print('正在获取',name,'代码',code)
        df = get_day(name,code,Kl.start_date,Kl.end_date)
        if len(df) > 0:
           df_dict.append({'df':df.to_dict(),'name':name,'code':code})

    save_stock_trader(df_dict)
    load_stock_trader(Kl)
