#
# Klang class
#
from . import data_zhanluejia as zhanluejia
from . import data_baostock as bs 
from .common import *
import copy

class Klang():
    def __init__(self):
        self.data_engine  = bs 
        self.start_date   = start
        self.end_date     = end
        self.df_all       = []
        self.stocklist    = []
        self.stockindex   = {}
        self.currentindex = 0
        self.currentdf    = {}
        self.dfstart      = "2021-01-01"
        self.dfend        = end
        self.reload       = False


    #df_all 是总的数据
    #每次加载的时候可以设置并且获取部分数据
    # copy.deepcopy 深度复制数据，以免破坏
    def setcurrent(self,code):
        self.currentindex = self.stockindex[code]
        self.currentdf = copy.deepcopy(self.df_all[self.currentindex])
        df = self.currentdf['df']
        df = df[self.dfstart:self.dfend] 
        self.currentdf['df'] = df
        
    def setdate(self,start="2021-01-01",end=end):
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
    def get_day(self):
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

    Kl.stocklist = bs.init_stock_list()
    Kl.get_day()

    #set default stock
    Kl.currentdf = Kl.df_all[0]    

