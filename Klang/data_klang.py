#
# klang.org.cn 提供的股票数据
# 数据来自baostock + tdx
# 数据提供模块来自 Kdata 项目
# 为了加速Klang运行，数据会被存到本地文件
# 并且加载到内存
#


import os
import shutil
import json
import requests
import time
import pandas as pd
from .common import end
from threading import Lock
from progress.bar import Bar

hostname="https://data.klang.org.cn/api"

session = requests.Session()

def gethostname():
   
    serveriplist = []
    url = 'https://www.klang.org.cn/api/sysconfigs?keyword=data&filter=1'
    resp = requests.get(url).json()
    for i in resp:
        if i['key'] == 'dataserver':
            serveriplist = i['value'].split(',')
    host = "http://" + serveriplist[0] + "/api"
    return host
    
hostname = gethostname()

class DataAPI():
    def __init__(self,host=hostname):
        self.host = host

    def get_stocklist(self):
        url = self.host + "/stocklists"
        return session.get(url)

    def get_factor(self,factorname,date=end):
        url = self.host + "/getfactors"
        return session.get(url,params={'factorname':factorname,'date':date})

filename_jsont = os.path.expanduser("~/.klang_stock_trader.json")
filename_sl = os.path.expanduser("~/.klang_stock_list.csv")

filename_jsont = os.path.normpath(filename_jsont)
filename_sl = os.path.normpath(filename_sl)

mutex = Lock()

#
#stock list
#['code','name','SCR','tdxbk','tdxgn']
stocklist=[]
stockindex={}
kapi = DataAPI()


def get_scr(code):
    index = stockindex[code]
    stock = stocklist[index]
    return stock.get('SCR',"50")

def get_chouma(code):
    return get_scr(code)
#
# extern to Klang
# 此接口有外部调用
#
def updatestockdata(Kl):
    global  stock_json_list

    stocklist = Kl.stocklist
    
    f = open(filename_jsont)

    for i in stocklist:
        content  = f.readline()
        if len(content) < 8:
            break
        stock    = json.loads(content[:-1])
        code     = stock[0]
        name     = stock[1]
        jsondata = stock[2]
        #print('正在获取',name,'代码',code)

        df = json_to_df(jsondata)
        if len(df) > 2:
           df['datetime'] = df['date']
           df = df.set_index('date')
        
        number = Kl.stockindex.get(code,None)
        if number is None:
            continue 
        Kl.df_all[number]["df"] = df
 
    f.close()


# 从服务器下载数据 同步存储到文件
def downloadstockdata(Kl):
    #创建临时文件
    f = open(filename_jsont+".tmp","w+")
    bar = Bar('Downloading ',max=len(Kl.stocklist))
    for stock in Kl.stocklist:
        code ,name = stock['code'],stock['name']
        jsondata,name,code = get_day(name,code,Kl.start_date,Kl.end_date,json=True)
        #print(code,name)
        content = json.dumps([code,name,jsondata])    
        f.write(content+"\n")
        f.flush()
        bar.next()
    bar.finish()
    f.close()

    #下载完成，生存目标文件         
    shutil.move(filename_jsont+".tmp",filename_jsont)

# 从klang获取日K数据
# append,是否追加到 股票列表
#
def get_day(name,code,start,end,setindex=False,json=False):
    
    #print(name,code)

    mutex.acquire()
    try:
        json_data = session.get(hostname+"/dayks",
            params={"code":code,"end":end,"limit":200},timeout=1000).json()
    except:
        time.sleep(2)
        json_data = session.get(hostname+"/dayks",
            params={"code":code,"end":end,"limit":200},timeout=1000).json()
   
    mutex.release()
    
    for d in json_data:
        del d["id"]
        del d["name"]
        del d["code"]
        del d["publishedAt"]
        del d["createdAt"]
        del d["updatedAt"]
        
    if json==True:
        return json_data,name,code
   
    return json_to_df(json_data,setindex)

def json_to_df(json,setindex=False):

    df = pd.json_normalize(json)
    if len(df) < 1:
       return []

    df = df[df['volume']>0.0] 
    # 删除后再次判断
    if len(df) < 1:
       return []


    #df = df.drop(columns=['_id','id'])
    datas = df.sort_values(by="date",ascending=True)


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



#
# 从网上下载数据或者从文件加载股票数据    
# 加载后数据存放在(Kl.df_all)
#
def get_all_day(Kl):    
    # 如果文件存在,可以直接从文件加载数据
    # 要强制从网上加载数据,可以设置reload=True
    if os.path.exists(filename_jsont) and not Kl.reload:
        print("正在从文件",filename_jsont,"加载数据")
        updatestockdata(Kl)
        return 

    print("正在从网上下载股票数据,时间将会有点长")
    downloadstockdata(Kl)
    updatestockdata(Kl)

def add_factor(name,order):
    result = kapi.get_factor(name).json()
    for i in result:
        code = i['code']
        index = stockindex.get(code,None)
        if index is None:
            continue        
        stocklist[index][name] = i['value'].split(",")[0]
    # tdxgn 有多个字段用 ',' 分开，所以要处理

def updatestocklist(stname=filename_sl):

    listjson = kapi.get_stocklist().json()
    index = 0
    for i in listjson:
        stocklist.append({"code":i['code'],"name":i['name'],"df":None})
        stockindex[i['code']] = index
        index += 1

    print("正在加载因子:筹码，板块 ")
    add_factor("SCR",2)
    add_factor("tdxbk",3)
    add_factor("tdxgn",4)
    print("因子加载完成")

    df = pd.json_normalize(stocklist)
    
    # 结果集输出到csv文件
    df.to_csv(stname, index=False,columns=['code','name','SCR','tdxbk','tdxgn'])  


def init_stock_list(Kl,offset=0):
    global stockindex,stocklist
   
    if not os.path.exists(filename_sl):
        print('正在下载股票库列表....')
        updatestocklist(filename_sl)
        print("股票列表下载完成")

    stocklist  = []
    print("正在从文件",filename_sl,"加载股票列表")
    stocklines = open(filename_sl,encoding='utf-8').readlines()
    stocklines = stocklines[1:] #删除第一行

    index = 0
    for i in stocklines:
        i = i.strip()
        code,name,scr,tdxbk,tdxgn = i.split(',')
        stocklist.append({"code":code,"name":name,"df":None,'SCR':scr,"tdxbk":tdxbk,"tdxgn":tdxgn})
        stockindex[code] = index
        index += 1

    #stocklist = stocklist[:100]
    # 初始化 code到index 对应表

    Kl.df_all = []
    for stock in stocklist:
            Kl.stockindex = stockindex
            Kl.df_all.append(stock) 

    return stocklist


