# Klang
stock K-line language 

Klang 是Kline语言,即股票语言,支持方便快捷的股票编程,可以轻松搞定股票公式

是股票编程和量化交易的必备工具

Klang 最大的亮点是支持中文编程,可以看最后的完整例子

任何问题欢迎访问[问答社区](https://forum.klang.org.cn)

# 在线试用
* 内置中文编程公式
你可以在线体验 Klang 编程, 无需安装,网站内置了多个选股公式 [Online](https://klang.org.cn/online.html)


# Klang 是股票K线形态语言,基于 python3
* 语言解释器采用 python的 ply库，他采用了flex，yacc语法的实现
* 股票数据来源 baostock,zhanluejia
* 支持 同花顺、通达信、文华财经等的公式, 感谢funcat 移植到了 Python 版本
* 支持结构形态 感谢talib
* Klang 语言是基于Python语法拓展了部分自己的语法，并且编写了快捷的股票公式 
* 支持网页直接使用,交互方便
* 支持中文编程,一看就懂
* 增加了股票特征计算

# install
* 安装过程中遇到talib错误，需要搜索talib源代码解决
```
git clone https://github.com/KlangAlpha/Klang
cd Klang
pip3 install -r requirements.txt 
python3 setup.py install
```

# 下载数据, 也可以直接使用不下载数据，下载数据约10分钟。
* 可以跳过，直接运行
* 下载数据有2种方法，第一种是直接下载压缩包，第二种是使用API下载

* 方法一、 推荐，适用于网络速一般的场景
```
python3 tools/download.py
```
* 方法二、 通过API下载
```
python3 update_data.py
```


# 应用示例 python  版本
* 第一次会下载数据,预计需要几分钟,推荐先用上面的步骤下载数据后再执行
* 具体例子可以看 test.py,testparse.py

```
from Klang import Klang,C,O
Klang.Klang_init()
Kl = Klang.Kl
C/C[1]

```
以上代码就快捷的计算了今日收盘价/昨日收盘价
默认计算第一个股票 sh.600000
今日收盘价，更新时间为下午5点左右

### 设置当前股票 'sh.601012','sz.000100'

```
Kl.code('sh.601012')
```
你也可以设置你想要的股票code

### 设置时间，周期默认是 2021-01-01开始
* 默认数据是日K

```
Kl.date(start='2022-04-02',end='2022-05-01')
```

### 显示收盘价

```
print(C.data) #显示已经下载周期的所有收盘价
print(O.data) #显示所有周日的开盘价
```

### 通过日期索引股票价格

```
print(C.['2022-05-20'])
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
from Klang import Klang
Klang.Klang_init()
# Klang和python的桥梁，支持函数,变量共享
# 具体使用方法 参见 testparse.py

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):    
    globals()[name]=val


setPY(getpyglobals,setpyglobals) 

```

###  执行 K语言语句
* 赋值
```
pi = 3.14 #python
Kexec("ABCD=pi+1;") #调用K语言执行，执行后K变量共享给了python

```
调用 Kexec执行Klang语法，Kexec参数里穿的字符串语法遵守Klang语法规则


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
* 兼容 := 赋值语法
* 支持兼容 python函数,getstockinfo等 getstockinfo是在python里面自定义的函数
* kloop,endp 是自定义语法，会遍历整个A股的股票，


### examples
* 使用了网页+websocket server模式
* server里调用 Kexec执行 所有的输入
* 默认的输入会扫描所有的A股4000多只股票
* 计算结果回传到网页界面显示

```
python3 kws_manager.py 
python3 kws_server.py
```

两个服务同时启动，可以Linux使用 "&" 放到后台
```
python3 kws_manager.py
```

* 如果kws_server.py启动出错可以有2中方法。
* 方法一、 安装Klang

```
python3 setup install
```

* 方法二、 打开kws_server.py里面注释,路径为Klang放置的地方
```
#sys.path.append(os.path.expanduser("~") + "/Klang")

```

浏览 online.html 即可运算公式了
# 支持中文编程

```

        涨停 = 9.9
        今日收盘 = C
        昨日收盘 = C[1]
        日期范围 = date
        显示 = DISPLAY
        ###############################
        # 参数涨停,表示涨幅的幅度
        # 以上为参数的值可以修改
        # 日期范围('2021-01-01','2021-06-25')
        ###############################

        实际涨幅 = (今日收盘-昨日收盘) / 昨日收盘
        实际涨幅 = 实际涨幅 * 100
        if 实际涨幅 > 涨停:
            显示(实际涨幅)
```

# 更新
* 2021.12.1 增加了特征提取公式
* 2021.7.3 增加了板块和概念信息，板块来自通达信


# 文件说明
```
├── Klang
│   ├── Kdatas.py               # 封装数据接口
│   ├── Kfeature.py             # 股票特征计算,形态计算
│   ├── Klang.py                # 主类
│   ├── __init__.py         
│   ├── common.py               # 公共设置
│   ├── data_klang.py           # 股票数据接口 klang.org.cn
│   ├── lang                    # Klang 编程语言目录
│   │   ├── __init__.py
│   │   ├── klex.py
│   │   ├── kparse.py
│   │   └── mAST.py             # 语言的解释
│   ├── talib_api.py            # 应用封装talib
│   └── tdx.py                  # 兼容 通达信公式
├── LICENSE
├── README.md
├── server
│   ├── online.html             # 在线使用的代码
│   └── wsserver.py             # 通过websocket和后台联系
├── requirements.txt
├── setup.py
├── test.py
└── testparse.py

```


