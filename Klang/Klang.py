#
# Klang class
#
from . import data_zhanluejia as zhanluejia
from . import data_baostock as bs 
from .common import *

class Klang():
    def __init__(self):
        self.data_engine  = bs 
        self.start_date   = start
        self.end_date     = end
        self.df_all       = []
        self.stocklist    = []
        self.stockindex   = {}
        self.currentindex = 0
        self.currentdf    = []
        self.reload       = False



    def setcurrent(self,code):
        self.currentindex = self.stockindex[code]
        self.currentdf = self.df_all[self.currentindex]

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



Kl = Klang()

def Klang_init():
    global Kl

    Kl.stocklist = bs.init_stock_list()
    Kl.get_day()
    Kl.currentdf = Kl.df_all[0]    

