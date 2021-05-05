#
# tdx 通达信相关的函数
#
tdx_datetime=None

def settdx(d):
    global tdx_datetime

    tdx_datetime=d

"""
返回无效数。
用法： DRAWNULL
"""
def DRAWNULL():
    return None

"""
REF 向前引用
引用若干周期前的数据。
用法：　REF(X，A)　引用A周期前的X值。
例如：　REF(CLOSE，1)　表示上一周期的收盘价，在日线上就是昨收。
"""
def REF(X,A):
    return X[A]


"""
引用指定日期的数据。
用法：　REFDATE(X，A)　引用A日期的X值。
例如：　REFDATE(CLOSE，20011208)　表示2001年12月08日的收盘价。
"""
def REFDATE(X,A):
    idx = ""
    for i in range(0,len(tdx_datetime)):
        if str(tdx_datetime[i]).replace("-","") == A:
            idx = i
            break

    if idx == "":
        return None
    return X[idx]


def iif(condition,result1,result2):
    if(condition):
        return result1
    else:
        return result2
