#
# K-line, stock datas 
#
import numpy as np
import pandas

kl = None
def setstock(kl1):
    global kl
    kl = kl1

"""
df2 = df[(df.date >= '2020-10-01') & 
             (df.date <= '2021-01-01')] 
"""

#获取股票数据
def getstockdata(name):
    if isinstance(kl.currentdf.get('df'),pandas.core.frame.DataFrame):
        return kl.currentdf['df'][name]
    return []
        
#做类似C/C[1]计算
#计算涨跌率
def match_size(*datas_list):
    size = min(len(data) for data in datas_list)
    if size == 0:
        return np.array([]),np.array([])
    #[len-size:]
    new_list = [np.array(data[len(data)-size:]) for data in datas_list]
    return new_list


#股票数据重新定义以方便计算

class Kdatas(object):
    def __init__(self,index=0):
        self._data = []
        self.currentindex = -1 #stock code index
        self.dfstart      = -1 #stock start date
        self.dfend        = -1 #stock end date
        self.index = index     #C,C[1],C[2]


    #返回最后一天的数据
    @property
    def value(self):
        return self.data[-1]

    #比较currentindex值的目的是切换股票的时候刷新
    @property
    def data(self):
        if len(self._data) == 0 or self.currentindex != kl.currentindex\
            or self.dfstart != kl.dfstart\
            or self.dfend   != kl.dfend:

            #reload
            self.currentindex = kl.currentindex
            self.dfstart = kl.dfstart
            self.dfend   = kl.dfend

            d = getstockdata(self.name).astype(self.dtype)
            index = len(d) - self.index
            if index > 0:
                self._data = d[:index]
            else :
                self._data = []
        return self._data

    #C,index=0,
    #C[1],index=1
    def __getitem__(self, index):
        n = self.__class__(index)
        if len(self._data) > index:
            nindex = len(self._data) - index
            n._data = self.data[:nindex]
        else:
            n._data = np.array([])
        return n

    def __truediv__(self, other):
        #s1 , s2 = match_size(self.data,other.data)
        return self.value / other.value

    __div__ = __truediv__

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return str(self.value)

# create open high low close volume date
for name in ["open", "high", "low", "close", "volume", "datetime"]:
    dtype = np.float64 if name != "datetime" else np.str_
    cls = type("{}Kdatas".format(name.capitalize()), (Kdatas, ), {"name": name, "dtype": dtype})
    obj = cls()
    for var in [name[0], name[0].upper(), name.upper()]:
        globals()[var] = obj

