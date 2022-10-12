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
from .common import end,get_date
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

def get_path(name):
    t = os.path.expanduser(name)
    return os.path.normpath(t)

data_path = get_path("~/.klang")
os.makedirs(data_path, exist_ok=True)

os.makedirs(get_path(data_path+"/day"), exist_ok=True)
os.makedirs(get_path(data_path+"/week"), exist_ok=True)
os.makedirs(get_path(data_path+"/month"), exist_ok=True)


filename_sl = get_path("~/.klang/klang_stock_list.csv")
file_updata_list = get_path("~/.klang/update_list.csv")


mutex = Lock()

#
#stock list
#['code','name','SCR','tdxbk','tdxgn']
stocklist=[]
stockindex={}
stockupdate={} # code, day, week, month ,日，周，月更新日期 
kapi = DataAPI()


def get_scr(code):
    index = stockindex[code]
    stock = stocklist[index]

    return stock.get('SCR',"50")

def get_chouma(code):
    return get_scr(code)

def save_stockupdate():
    buf = json.dumps(stockupdate)
    f1 = open(file_updata_list,"w+")
    f1.write(buf)
    f1.close()

def json_to_df(json,setindex=False):

    df = pd.json_normalize(json)
    if len(df) < 1:
       return []

    df = df[df['volume']>0.0] 
    # 删除后再次判断
    if len(df) < 1:
       return []

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


       

class GetData:
    def __init__(self,freq="d"):
        self.freq = self._name(freq)


    def _name(self,_name):
        name_table = {"day":"d","d":"d",
                            "week":"w","w":"w",
                            "month":"m","m":"m"}
        self.freq = name_table.get(_name,"d")
        return self.freq #默认是 d

    def append_data(self,code,content):
        ext_table = {"d":"day","w":"week","m":"month"}
        ext = ext_table.get(self.freq,"day")

        # 可能是文件不存在的情况
        try:
            f1 = open(get_path("~/.klang/"+ ext + "/"+code+ ext + ".json"),"r")
            content1 = f1.read()
            f1.close()

            stock    = json.loads(content1)
            jsondata = stock[2]
        #print('正在获取',name,'代码',code)
        except:
            jsondata = []

        df = pd.json_normalize(content+jsondata)
        df1 = df[~df.date.duplicated(keep='first')]
        return json.loads(df1.to_json(orient="records"))
    
 

    def _read_file_data(self,code):
        ext_table = {"d":"day","w":"week","m":"month"}
        ext = ext_table.get(self.freq,"day")

        if not os.path.exists(get_path("~/.klang/"+ext +"/" +code+ ext + ".json")):
            return pd.DataFrame([])

        f1 = open(get_path("~/.klang/"+ ext + "/"+ code+ ext + ".json"),"r")

        content = f1.read()
        f1.close()
        stock    = json.loads(content)
        jsondata = stock[2]
        #print('正在获取',name,'代码',code)
        df = json_to_df(jsondata)
        df['datetime'] = df['date']
        df = df.set_index('date')
        return df

    def _read_server_data(self,code,start,end,setindex=False,json=False,append=False):
        ext_table = {"d":"/dayks","w":"/weeks","m":"/months"}
        ext_path = ext_table.get(self.freq,"/days")

        if append == True:
            params = {"code":code,"start":start,"limit":200}
        else:
            params = {"code":code,"end":end,"limit":200}
        mutex.acquire()
        try:
            json_data = session.get(hostname+ ext_path,
                params=params,timeout=1000).json()
        except:
            time.sleep(2)
            json_data = session.get(hostname+ ext_path,
                params= params,timeout=1000).json()
        mutex.release()
        for d in json_data:
            del d["id"]
            del d["name"]
            del d["code"]
            del d["publishedAt"]
            del d["createdAt"]
            del d["updatedAt"]

        if json==True:
            return json_data

        return json_to_df(json_data,setindex)

    # 下载数据并且全部更新
    def down_and_save(self,Kl,code,start,end):

        ext_table = {"d":"day","w":"week","m":"month"}
        ext = ext_table.get(self.freq,"day")

        name = Kl.stockdict[code]['name']
        # 1. 从服务器下载数据
        jsondata = self._read_server_data(code,start,end,json=True)

        # 2. 保存到本地硬盘，
        content = json.dumps([code,name,jsondata])
        f1 = open(get_path("~/.klang/"+ ext +"/" + code+ ext + ".json"),"w+")
        f1.write(content)
        f1.close()

        # 3. 升级更新文件
        if  stockupdate.get(code,None) is None:
            stockupdate[code] = {}

        stockupdate[code][ext] = get_date(0)
        save_stockupdate()
        return jsondata

    def get_data(self,Kl,code,start,end):
        df = self._read_file_data(code)
        if len(df) < 1:
            jsondata = self.down_and_save (Kl,code,start,end)
            df = json_to_df(jsondata,setindex=True)

        return df

    # 下载数据 更新数据，只做差异补偿

    def update_data(self,Kl,code,check=True):
        ext_table = {"d":"day","w":"week","m":"month"}
        ext = ext_table.get(self.freq,"day")

        if not os.path.exists(get_path("~/.klang/"+ext+"/" +code+ ext + ".json")):
            return self.get_data(Kl,code,Kl.start_date,Kl.end_date)
        
        today = get_date(0)

        name = Kl.stockdict[code]['name']
        lastday = stockupdate.get(code,{}).get(ext,'2021-01-01')
        if lastday == today and check:
            return 
        jsondata = self._read_server_data(code,lastday,Kl.end_date,json=True,append=True)
        jsondata = self.append_data(code,jsondata)

        content = json.dumps([code,name,jsondata])
        f1 = open(get_path("~/.klang/"+ ext +"/" +code+ ext+ ".json"),"w+")
        f1.write(content)
        f1.close()

        if  stockupdate.get(code,None) is None:
            stockupdate[code] = {}

        stockupdate[code][ext] = get_date(0)
        

# 下载所有的股票
def downloadstockdata(Kl):

    bar = Bar('Downloading ',max=len(Kl.stocklist))
    bar.is_tty = lambda :True
    today = get_date(0)
    for stock in Kl.stocklist:

        code = stock['code']
        day_data.down_and_save(Kl,code,Kl.start_date,Kl.end_date)
        week_data.down_and_save(Kl,code,Kl.start_date,Kl.end_date)
        month_data.down_and_save(Kl,code,Kl.start_date,Kl.end_date)

        save_stockupdate()
        bar.next()
    bar.finish()
    save_stockupdate()

# 更新所有的股票
# 更新仅仅更新日K，下载是下载日，月，周
def updatestockdata(Kl,check=True):

    bar = Bar('Downloading ',max=len(Kl.stocklist))
    bar.is_tty = lambda :True
    today = get_date(0)
    for stock in Kl.stocklist:
        code = stock['code']

        day_data.update_data(Kl,code,check)
        #week_data.update_data(Kl,code,check)
        #month_data.update_data(Kl,code,chedk)

        save_stockupdate()
        bar.next()
    bar.finish()
    save_stockupdate()



#
# 从网上下载数据或者从文件加载股票数据    
# 加载后数据存放在(Kl.df_all)
#
def get_all_data(Kl):    
    updatestockdata(Kl,check=True) # 检查更新和追加数据

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
    global stocklist,stockupdate
   
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
        Kl.stockdict[code]  = {"name":name,'SCR':scr,"tdxbk":tdxbk,"tdxgn":tdxgn,"index":index}
        stockindex[code] = index
        index += 1

    #
    # 获取股票 更新列表
    #
    if os.path.exists(file_updata_list):
        f = open(file_updata_list)
        stockupdate = json.load(f)
        f.close()

    return stocklist

day_data   = GetData(freq="d")
week_data  = GetData(freq="w")
month_data = GetData(freq="m")

