#
# Klang class
# Klang 提供了全局的股票数据，和获取股票数据的方法
# Kdatas 是提供了单只股票的数据和计算方法
#
from . import data_zhanluejia as zhanluejia
from . import data_baostock as bs 
from .common import * #start,end date
import copy
import threading

class Klang():
    def __init__(self):
        self.data_engine  = bs 
        self.start_date   = start #common.py
        self.end_date     = end   #common.py
        self.df_all       = [] #所有的股票,name:股票名称，code：股票代码，df，股票数据
        self.stocklist    = []
        self.stockindex   = {} #股票代码对应的索引需要
        self.currentindex = 0  #当前选择的股票在数组中的序号
        self.currentdf    = {} #当前选择的股票pandas格式数据
        self.dfstart      = "2021-01-01"
        self.dfend        = end
        self.reload       = False



    # 为了防止数据加载过慢,
    # 做了检查为加载的股票并加载
    def getdatabycode(self,code):
        index = self.stockindex[code]

        #如果没有数据需要加载
        if self.df_all[index]['df'] is None:
            print ("正在加载数据请稍后")
            self.df_all[index]['df'] = self.data_engine.get_day(
                self.df_all[index]['name'],
                self.df_all[index]['code'],
                self.start_date,
                self.end_date,
                True # set index = date
            )


    #df_all 是总的数据
    #每次加载的时候可以设置并且获取部分数据
    # copy.deepcopy 深度复制数据，以免破坏
    def setcurrent(self,code):
        self.getdatabycode(code)
        self.currentindex = self.stockindex[code]
        self.currentdf = copy.deepcopy(self.df_all[self.currentindex])

        df = self.currentdf['df']
        df = df[self.dfstart:self.dfend] 
        self.currentdf['df'] = df
        
    def setdate(self,start="2021-01-01",end=end):
        code = self.df_all[self.currentindex]['code']
        self.getdatabycode(code)

        self.dfstart=start
        self.dfend=end
        # 重新获取数据
        self.currentdf = copy.deepcopy(self.df_all[self.currentindex])
        df = self.currentdf['df']
        df = df[self.dfstart:self.dfend] 
        self.currentdf['df'] = df
 

    """
    获取所有的A股的日K数据
    """
    def get_all_day(self):
        self.data_engine.get_all_day(self)   

    """
    升级股票列表
    A 股目前有4000多只股票    
    股票列表存储到stock_list.csv文件
    """
    def updatestock(self):
        bs.updatestock()


#
# 循环计算所有股票，把满足表达式的显示出来
#
def search(condition,printf=print):
    #save old state

    for i in Kl.df_all:
        pass

    #restore old state

Kl = Klang()

def Klang_init():
    global Kl

    #初始化股票列表，并且把name，code放到 df_all，此时df为加载
    Kl.stocklist = bs.init_stock_list(Kl)

    #异步加载df 放到df_all
    t = threading.Thread(target=Kl.get_all_day)
    t.start()
    
    #set default stock
    Kl.setdate(start='2021-01-01')
    Kl.currentdf = Kl.df_all[0]    

