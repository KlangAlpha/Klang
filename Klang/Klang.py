#
# Klang class
# Klang 提供了全局的股票数据，和获取股票数据的方法
# Kdatas 是提供了单只股票的数据和计算方法
#
from . import data_klang as datakl
from .common import * 
import copy
import threading

class Klang():
    def __init__(self):
        self.data_engine  = datakl #klang data server
        # 加载数据时 设置的加载时间范围
        self.start_date   = start #common.py
        self.end_date     = end   #common.py 全部数据的最后交易周期
        self.stocklist    = []
        self.stockdict    = {} # {code:name} code to name
        self.day_df       = None  #当前选择的股票pandas格式数据
        self.week_df       = None  #当前选择的股票pandas格式数据
        self.month_df       = None  #当前选择的股票pandas格式数据
        self.cur_code     = None
        self.cur_name     = None
        #某次计算过程中 需要的数据片段
        self.dfstart      = "2021-01-01"
        self.dfend        = end #当前要计算的交易周期
        self.reload       = False
        



    #df_all 是总的数据
    #每次加载的时候可以设置并且获取部分数据
    # copy.deepcopy 深度复制数据，以免破坏
    def code(self,code):
        self.cur_code = code
        self.cur_name = self.stockdict[code]['name']
        df = self.data_engine.day_data.get_data(self,code,self.start_date,self.end_date)
        df = df[self.dfstart:self.dfend] 
        self.day_df = df

    def date(self,start="2021-01-01",end=end):

        self.dfstart=start
        self.dfend=end

        df = self.data_engine.day_data.get_data(self,self.cur_code,self.start_date,self.end_date)
        df = df[self.dfstart:self.dfend] 
        self.day_df = df

    # 筹码 scr
    def chouma(self):
        return self.data_engine.get_scr(self.cur_code)
    
    """
    获取所有的A股的日K数据
    """
    def get_all_data(self):
        self.dfend = get_date(0)
        self.end_date = get_date(0)
        self.data_engine.get_all_data(self)   

    # 重新下载所有的数据
    def downloadall(self):
        self.data_engine.updatestocklist() #下载列表到文件
        self.stocklist = self.data_engine.init_stock_list(self) #加载

        self.data_engine.downloadstockdata(self,reload = True)

Kl = Klang()

def Klang_init():
    global Kl

    #初始化股票列表，并且把name，code放到 df_all，此时df为加载
    Kl.stocklist = Kl.data_engine.init_stock_list(Kl)

    #异步加载df 放到df_all
    t = threading.Thread(target=Kl.get_all_data)
    t.start()

    Kl.cur_code = Kl.stocklist[0]['code']    
    Kl.cur_name = Kl.stocklist[0]['name']    
    #set default stock
    Kl.date(start='2021-01-01')
    Kl.code(Kl.cur_code)

    
