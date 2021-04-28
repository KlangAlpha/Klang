#
# K-line, stock datas 
#
import numpy as np
import pandas

kl = None
def setstock(kl1):
    global kl
    kl = kl1

def getstockdata(name):
    if isinstance(kl.currentdf.get('df'),pandas.core.frame.DataFrame):
        return kl.currentdf['df'][name]
    return []
        

def match_size(*datas_list):
    size = min(len(data) for data in datas_list)
    if size == 0:
        return np.array([]),np.array([])
    new_list = [np.array(data[:size]) for data in datas_list]
    return new_list

class Kdatas(object):
    def __init__(self):
        self._data = []

    @property
    def data(self):
        if len(self._data) == 0:
            self._data = getstockdata(self.name).astype(self.dtype)
        return self._data

    def __getitem__(self, index):
        n = self.__class__()
        if len(self._data) > index:
            n._data = self._data[index:]
        else:
            n._data = np.array([])
        return n

    @property
    def value(self):
        pass 

    def __truediv__(self, other):
        s1 , s2 = match_size(self.data,other.data)
        return s1 / s2

    __div__ = __truediv__


# create open high low close volume date
for name in ["open", "high", "low", "close", "volume", "date"]:
    dtype = np.float64 if name != "date" else np.uint64
    cls = type("{}Kdatas".format(name.capitalize()), (Kdatas, ), {"name": name, "dtype": dtype})
    obj = cls()
    for var in [name[0], name[0].upper(), name.upper()]:
        globals()[var] = obj

