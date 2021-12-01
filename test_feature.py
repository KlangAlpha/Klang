import pandas as pd
from Klang import Kl
from Klang import SequenceTransformer

df = Kl.data_engine.get_day("五矿稀土",'sz.000831','2021-01-01','2021-12-01')


st_num = SequenceTransformer(addcalc=[
{'name':'ma','fname':'ma10','param':10},
{'name':'ma','fname':'ma20','param':20},
{'name':'ma','fname':'ma30','param':30},
])
print(st_num.transform(df['close']))
