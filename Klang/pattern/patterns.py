import pandas as pd
import numpy as np
from .zigzag_lib import peak_valley_pivots_np


def create_index(pivots):
    index_list = []
    for i in range(0,len(pivots)):
        if pivots[i] != 0:
            index_list.append(i)
    return index_list

# 尾部为上升趋势
def pattern_tail_rise():
    if pivots[pv_index[-1]] == 1 and pivots[pv_index[-2]] == -1:
        return 1
    return 0

# 杯和柄模式
def pattern_cup_handle():
    if len(pv_index) < 6:
        return 0 
    close = loaded_data['close'].values
    ret = 0
    for i in range(0,len(pv_index)-6):
        x1 = pv_index[i]
        a = pv_index[i+1]
        b = pv_index[i+2]
        c = pv_index[i+3]
        d = pv_index[i+4]
        e = pv_index[i+5]
        # a,c 杯沿差不多高，杯底b，比杯柄低，回调不能超过杯底部1/3
        ab = close[a] - close[b]
        cb = close[c] - close[b]
        cd = close[c] - close[d]
        if pivots[x1] == -1 and cb > 0 and abs(ab-cb)/cb < 0.15 and \
            close[b] < close[d] and \
            cb / 3 > cd: 
            #ax.text(a+1,close[a],"<-A")
            #ax.text(c+1,close[c],"<-C")
            #ax.annotate('', xy=(c, close[c]),xytext=(b, close[b]),\
            #    arrowprops=dict(color='blue', arrowstyle='-',connectionstyle="arc3,rad=0.4"))
            #ax.annotate('', xy=(b, close[b]),xytext=(a, close[a]),\
            #    arrowprops=dict(color='blue', arrowstyle='-',connectionstyle="arc3,rad=0.4"))
            ret = 1

    return ret

# W 底部
def pattern_w_bottom():
    if len(pv_index) < 5:
        return 0 
    ret = 0
    close = loaded_data['close'].values
    for i in range(0,len(pv_index)-5):
        a = pv_index[i]
        b = pv_index[i+1]
        c = pv_index[i+2]
        d = pv_index[i+3]
        e = pv_index[i+4]
        ab = close[a] - close[b]
        ad = close[a] - close[d]

        # b,d 为双底，a，e为顶
        if pivots[a] == 1 and APPROX(ab,ad,0.05) and \
            ab / close[b] > 0.2 :
            #ax.text(b+1,close[b],"<-B")
            #ax.text(d+1,close[d],"<-D")
            ret = 1
    return ret

# 三次底部
def pattern_triple_bottom():
    if len(pv_index) < 6:
        return 0 
    ret = 0
    close = loaded_data['close'].values
    for i in range(0,len(pv_index)-6):
        a = pv_index[i]
        b = pv_index[i+1]
        c = pv_index[i+2]
        d = pv_index[i+3]
        e = pv_index[i+4]
        f = pv_index[i+5]
        ab = close[a] - close[b]
        ad = close[a] - close[d]
        af = close[a] - close[f]

        # b,d,f 为三底，a，e为顶
        if pivots[a] == 1 and APPROX(ab,ad,0.05) and \
            APPROX(ab,af,0.05) and ab / close[b] > 0.2 :
            #ax.text(b+1,close[b],"<-B")
            #ax.text(d+1,close[d],"<-D")
            #ax.text(f+1,close[d],"<-F")
            ret = 1
    return ret

# 上攻回调买入
def pattern_dip():
    if len(pv_index) < 3:
        return 0 
    ret = 0
    close = loaded_data['close'].values
    last_index = pv_index[-5:]
    for i in range(0,len(last_index)-2):
        a = last_index[i]
        b = last_index[i+1]
        c = last_index[i+2]
        ba = close[b] - close[a]
        bc = close[b] - close[c]
        # a 为起涨点，b为高点，c为回调点,跌幅不能超过50%
        if pivots[a] == -1 and ba / close[b] > 0.3 and bc / ba < 0.5:
            #ax.text(a+1,close[a],"<-A")
            #ax.text(b+1,close[b],"<-B")
            #ax.text(c+1,close[c],"<-C")
            ret = 1

    return ret 

pivots = peak_valley_pivots_np(loaded_data['close'].values,step=3)
pv_index = create_index(pivots)

func_list= {"cup_handle":pattern_cup_handle,
            "w_bottom":pattern_w_bottom,
            "triple":pattern_triple_bottom,
            "dip":pattern_dip}

func = func_list.get(func_name,lambda:1)
    

