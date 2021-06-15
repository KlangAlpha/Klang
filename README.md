# Klang
stock K-line language 

# Klang 是股票K线形态语言,基于 python3
* 股票数据来源 baostock,zhanluejia
* 支持 同花顺、通达信、文华财经等的公式, 感谢funcat 移植到了 Python 版本
* 支持结构形态 感谢talib

# install
```
pip3 install -r requirements.txt 
```

# 应用示例
* 第一次会下载数据
```
from Klang import *

C/C[1]

```

# Klang 语言(K浪)
* testparse.py 代码片段
```
kloop
ret = CROSS(C,MA(C,60))
ma5 := MA(C,5)
ma10 = MA(C,10)
ma20 = MA(C,20)
ma60 = MA(C,60)

ret1 = (C - C[1])/C[1]
ret2 = (C - C[1])/C[1] > 0.05
info = getstockinfo(0)

if ma60[-1] < ma20[-1] and ma20[-1] < ma10[-1] and ma10[-1] < ma5[-1] and ret2 :
    print(info,ret1*100)

endp
print("计算完成")
```

# 支持列表
* 逐步兼容通达信公式，C,MA,CROSS
* 兼容 := 负值语法
* 支持兼容 python函数,getstockinfo等 getstockinfo是在python里面自定义的函数
* kloop,endp 是自定义语法，会遍历整个A股的股票，

