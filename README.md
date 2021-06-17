# Klang
stock K-line language 

# Klang 是股票K线形态语言,基于 python3
* 语言解释器采用 python的 ply库，他是flex，yacc语法的实现
* 股票数据来源 baostock,zhanluejia
* 支持 同花顺、通达信、文华财经等的公式, 感谢funcat 移植到了 Python 版本
* 支持结构形态 感谢talib

# install
```
pip3 install -r requirements.txt 
```

# 应用示例 python  版本
* 第一次会下载数据,预计需要几分钟
```
from Klang import *

C/C[1]

```

### 设置当前股票 'sh.601012','sz.000100'

```
Kl.code('sh.601012')
```

### 设置时间，周期默认是 2021-01-01开始
* 默认数据是日K

```
Kl.date(start='2021-04-02',end='2021-05-01')
```

### 显示收盘价

```
print(C.data) #显示已经下载周期的所有收盘价
print(O.data) #显示所有周日的开盘价
```

### 收盘价涨幅

```
print((C-C[1])/C[1]) #当前周期的收盘 比上一个周一的收盘价涨跌比率
```

### REF 和通达信兼容，获取之前周期的价格

```
REF(C,5) # 5周期前的收盘价，5日前收盘价
```

### 同时实现了MA,SMA,HHV,LLV,ABS等


# Klang 语言(K浪)
* testparse.py 代码片段

```
from Klang.lang import kparser,setPY,Kexec

# 共享Klang和python的变量，函数等

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):    
    globals()[name]=val


setPY(getpyglobals,setpyglobals) 

```
###  执行 K语言语句
* 负值
```
pi = 3.14 #python
Kexec("ABCD=pi+1;") #调用K语言执行，执行后K变量共享给了python

```

### 执行一段代码
* 详细例子参见 testparse.py
* 这里我们定制了一段kloop...endp，表示循环计算所有的A股
```
testblock=\
"""
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
"""

Kexec(testblock)

```



### 支持功能列表
* 逐步兼容通达信公式，C,MA,CROSS
* 兼容 := 负值语法
* 支持兼容 python函数,getstockinfo等 getstockinfo是在python里面自定义的函数
* kloop,endp 是自定义语法，会遍历整个A股的股票，

