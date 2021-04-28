import baostock as bs
import pandas as pd
import os
import json

bs.login()


filename_sl = os.path.expanduser("~/.klang_stock_list.csv")
filename_st = os.path.expanduser("~/.klang_stock_trader.csv")

#
#stock list
#
def updatestock(name=filename_sl):
    rs = bs.query_stock_industry()

    # 打印结果集
    industry_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        row = rs.get_row_data()
        kdata = bs.query_history_k_data_plus(row[1], 
                                      'date,open,high,low,close,volume', 
                                      start_date='2021-04-20',
                                      frequency='d')
        if len(kdata.get_row_data()) == 0:
            continue
        print(row)
        industry_list.append(row)
    result = pd.DataFrame(industry_list, columns=rs.fields)
    # 结果集输出到csv文件
    result.to_csv(name, index=False)    

def init_stock_list(offset=0):
    if not os.path.exists(filename_sl):
        print('正在下载股票库列表....')
        updatestock(filename_sl)
        print("股票列表下载完成")

    print("正在从文件",filename_sl,"加载股票列表")
    stocklist = open(filename_sl).readlines()
    stocklist = stocklist[1+int(offset):] #删除第一行
    return stocklist

#
# all stock trader day K data
#
def save_stock_trader(df_dict):
    content = json.dumps(df_dict)    
    f = open(filename_st,"w+")
    f.write(content)
    f.close()

def load_stock_trader(Kl,name=filename_st):
    content = open(name).read()

    df_dict = json.loads(content)
    number = 0
    for stock in df_dict:
        for name in stock:

            # save order for index
            code = stock[name]['code']['0']
            Kl.stockindex[code] = number
            number += 1

            # save df to list
            Kl.df_all.append({"name":name,"df":pd.DataFrame.from_dict(stock[name])}) 


#从bs获取日K数据
def get_day(name,code,start,end):
    rs = bs.query_history_k_data_plus(code, 
                                      'date,open,high,low,close,volume,code,turn', 
                                      start_date=start,
                                      end_date=end,frequency='d' )
    datas = rs.get_data()
    if len(datas) < 2:
        return []
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

    print("正在从网上下载股票数据")
    for stock in stocklist:
        code ,name = getstockinfo(stock)
        print('正在获取',name,'代码',code)
        df = get_day(name,code,Kl.start_date,Kl.end_date)
        if len(df) > 0:
           df_dict.append({name:df.to_dict()})

    save_stock_trader(df_dict)
    load_stock_trader(Kl)
