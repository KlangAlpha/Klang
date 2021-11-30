#
# feature 主要是股票形态和特征计算
# 连续性数据预测可以通过时序提取特征
# Klang 的特征参考了下面的工程
# tsfresh 里feature_calculators 
# talib 里股票特征计算
#
# Date: 2021-11
#




from .Kdatas import * 
from .talib_api import *
from .tdx import * 

# 波动率函数
# h 指 最高值
# l 指 最低值
# n 指 周期
# 返回 波动范围

def volatility(h1,l1,N):
    #周期不够，用当前h1周期计算
    if N > len(h1):
        N = len(h1)

    max_h = HHV(h1,N)

    min_l = LLV(l1,N)
    
    return ((max_h - min_l) / min_l ) * 100

# 横盘震荡
# 默认是 60周期
# 默认h1 是 HIGH
# 默认l1 是low
# 默认返回 波动率
# transverse

def TRANSVERSE(h1=HIGH,l1=LOW,N=60,R=None):
    r = volatility(h1,l1,N)

    # 如果没有设置震荡参数，
    # 返回波动率
    if R is None:
        return r

    # 如果设置了震荡参数
    # 返回是否是震荡
    if r <= R:
        return True
    return False



# 本段代码参考了 smoothnlp/seq2ftr
# 都是参考了 tsfresh或者复制了tsfresh 代码

import hashlib
from functools import wraps
def set_property(*args):
    """
    The decorators for set properties for individual feature calculators
    :param args:
        name: the function's name for display
        stype: the supporting types for the feature calculating function
             0 for boolean, 1 for numericla, 2 for categorical
    :return:
    """
    def decorate_func(func):
        for i in range(0,len(args),2):
            setattr(func, args[i], args[i+1])
        return func
    return decorate_func

def listify_type(func):
    """
    Decorator for casting input to list
    :param func:
    :return:
    """
    @wraps(func)
    def listify(*args):
        x = args[0]
        if not isinstance(x,list):
            x = list(x)
        return func(x)
    return listify

def filter_none(func):
    """
    filter None value in input list
    :param func:
    :return:
    """
    @wraps(func)
    def filterfunc(*args):
        x = args[0]
        x = [a for a in x if a is not None]
        return func(x)
    return filterfunc

##########################
## Supporting Funcitons ##
##########################
def _shift(x:list,n:int):
    """
    works similar to np.roll
    :param x:
    :param n:
    :return:
    """
    return x[n:]+x[:n]

def _sort(x:list):
    x_copy = x.copy()
    x_copy.sort()
    return x_copy
global x_sorted

def _appearance_count(x:list):
    """
    get frequency count
    :param x:
    :return:
    """
    freq = {k:0 for k in set(x)}
    for xi in x:
        freq[xi]+=1
    return freq
global x_freq_count

def _token_hash(x:list):
    """
    get input hash result
    :param key:
    :return:
    """
    if isinstance(x, str):
        x_md5 = hashlib.md5(x.encode("utf-8")).hexdigest()
        y = [int(v) for v in list(x) if v.isdigit()]
        y = sum(y)
        x_hash = hash(y)
    else:
        x_hash = hash(x)
    return x_hash

def _z_transform(x:list):
    xmean = _mean(x)
    xstd = _std(x)
    return [(xi-xmean)/xstd for xi in x]


#########################
## Feature Calculators ##
#########################
@set_property("name","mean","stypes",[0,1])
@listify_type
@filter_none
def _mean(x:list):
    return sum(x)/len(x)

@set_property("name","max","stypes",[0,1])
@listify_type
@filter_none
def _max(x:list):
    return max(x)

@set_property("name","freq_of_max","stypes",[1])
@filter_none
def _freq_of_max(x:list):
    max_x = _max(x)
    return len([xi for xi in x if xi >=max_x])

@set_property("name","min","stypes",[0,1])
@listify_type
@filter_none
def _min(x:list):
    return min(x)

@set_property("name","freq_of_min","stypes",[1])
@filter_none
def _freq_of_min(x:list):
    min_x = _min(x)
    return len([xi for xi in x if xi<=min_x])

@set_property("name",'median',"stypes",[1])
@listify_type
@filter_none
def _median(x:list):
    x_sorted = _sort(x)
    x_len = len(x_sorted)
    if x_len%2==1:
        return x_sorted[x_len//2]
    else:
        return x_sorted[x_len//2]*0.5 + x_sorted[x_len//2-1]*0.5

@set_property("name","median_mean_distance","stypes",[1])
@filter_none
def _median_mean_distance(x:list):
    return abs(_mean(x)-_median(x))/(_max(x)-_min(x))

@set_property("name","percentage_below_mean","stypes",[1])
@filter_none
def _percentage_below_mean(x:list):
    x_mean = _mean(x)
    return len([xi for xi in x if xi<x_mean])/_len(x)

@set_property("name","variance","stypes",[1])
@filter_none
def _var(x:list):
    avg = _mean(x)
    return sum([(xi-avg)**2 for xi in x])/len(x)

@set_property("name","standard_deviation","stypes",[1])
@filter_none
def _std(x:list):
    return _var(x)**(0.5)

@set_property("name","uniqueCount","stypes",[0,1,2])
@listify_type
@filter_none
def _uniqueCount(x:list):
    return len(set(x))

@set_property("name","length","stypes",[0,1,2])
@listify_type
@filter_none
def _len(x:list):
    return len(x)

@set_property("name","duplicates_count","stypes",[0,1,2])
@filter_none
def _num_duplicates(x:list):
    return _len(x) - _uniqueCount(x)+1

@set_property("name","flucturate_rate","stypes",[0,2])
@listify_type
@filter_none
def _flucturate_rate(x:list,shift=1):
    x_shifted = _shift(x,shift)
    flucturate_vec = [xi1==xi2 for xi1,xi2 in zip(x[:-shift],x_shifted[:-shift])]
    return sum(flucturate_vec)/(len(x)-shift)

@set_property("name","percentage_of_most_reoccuring_value_to_all_values","stypes",[1,2])
@listify_type
@filter_none
def _percentage_of_most_reoccuring_value_to_all_values(x:list):
    x_freq_count = _appearance_count(x)
    return 1/len(x_freq_count)

@set_property("name","percentage_of_most_reoocuring_value_to_all_datapoints","stypes",[1,2])
@listify_type
@filter_none
def _percentage_of_most_reoocuring_value_to_all_datapoints(x:list):
    x_freq_count = _appearance_count(x)
    return max(x_freq_count.values()) / len(x)

@set_property("name","last_location_of_max","stypes",[1])
@filter_none
def _last_location_of_max(x:list):
    xmax = _max(x)
    for i in range(1,len(x)+1):
        if x[-i] == xmax:
            return i

@set_property("name","fist_location_of_max","stypes",[1])
@filter_none
def _first_location_of_max(x:list):
    xmax = _max(x)
    for i in range(len(x)):
        if x[i] == xmax:
            return i

@set_property("name","last_location_of_min","stypes",[1])
@filter_none
def _last_location_of_min(x:list):
    xmin = _min(x)
    for i in range(1,len(x)+1):
        if x[-i] == xmin:
            return i

@set_property("name","fist_location_of_min","stypes",[1])
@filter_none
def _first_location_of_min(x:list):
    xmin = _min(x)
    for i in range(len(x)):
        if x[i] == xmin:
            return i

@set_property("name","ratio_value_number_to_seq_length","stypes",[1,2])
@filter_none
def _ratio_value_number_to_seq_length(x:list):
    return len(set(x))/_len(x)

@set_property("name","number_peaks_1","stypes",[1])
@listify_type
@filter_none
def _number_peaks(x,n=1):
    counter = 0
    for i in range(n,len(x)-n):
        neighbors=[x[i-j] for j in range(1,n+1)] + [x[i+j] for j in range(1,n+1)]
        if x[i] > max(neighbors):
            counter+=1
    return counter

@set_property("name","number_peaks_2","stypes",[1])
@filter_none
def _number_peaks2(x:list):
    return _number_peaks(x,2)


@set_property("name","number_peaks_3","stypes",[1])
@filter_none
def _number_peaks3(x:list):
    return _number_peaks(x,3)

@set_property("name", "skewness", "stypes", [1])
@listify_type
@filter_none
def _skewness(x:list):
    avg = _mean(x)
    adjusted = [v - avg for v in x]
    count = len(x)
    adjusted2 = [pow(v,2) for v in adjusted]
    adjusted3 = [adjusted2[i] * adjusted[i] for i in range(len(adjusted))]
    m2 = sum(adjusted2)
    m3 = sum(adjusted3)

    if count<3:
        return None
    else:
        if m2 == 0:
            return 0
        else:
            result = (count * (count -1) ** 0.5 / (count - 2)) * (m3 / m2 ** 1.5)
            return round(result, 6)

@set_property("name","kurtosis", "stypes", [1])
@listify_type
@filter_none
def _kurtosis(x:list):
    avg = _mean(x)
    count = len(x)
    adjusted = [v - avg for v in x]
    adjusted2 = [pow(v,2) for v in adjusted]
    adjusted4 = [pow(v,2) for v in adjusted2]
    m2 = sum(adjusted2)
    m4 = sum(adjusted4)

    if count<4:
        return None
    else:
        adj = 3 * (count -1) ** 2 / ((count -2) * (count-3))
        numer = count * (count + 1) * (count - 1) * m4
        denom = (count - 2) * (count - 3) * m2 ** 2
        if denom == 0:
            return 0
        else:
            return round(numer/denom - adj, 6)

@set_property("name","abs_energy","stypes",[1])
@listify_type
@filter_none
def _abs_energy(x:list):
    """
      .. math::
        E = \\sum_{i=1,\ldots, n} x_i^2
    :param x:
    :return:
    """
    return sum([xi**2 for xi in x])

@set_property("name","cid_ce","stypes",[1])
@filter_none
def _cid_ce(x:list):
    """
    .. math::
        \\sqrt{ \\sum_{i=0}^{n-2lag} ( x_{i} - x_{i+1})^2 }
    .. rubric:: References
    |  [1] Batista, Gustavo EAPA, et al (2014).
    |  CID: an efficient complexity-invariant distance for time series.
    :param x:
    :return:
    """
    x_z_transformed = _z_transform(x)
    return _abs_energy(x_z_transformed)**(0.5)

@set_property("name","mean_change","stypes",[1])
@filter_none
def _mean_change(x):
    x_rolled = _shift(x,1)
    x_diff = [xi-xj for xi,xj in zip(x,x_rolled)]
    return _mean(x_diff)

@set_property("name","min_change","stypes",[1])
@filter_none
def _mean_change(x):
    x_rolled = _shift(x,1)
    x_diff = [xi-xj for xi,xj in zip(x,x_rolled)]
    return _min(x_diff)


@set_property("name","_ndex_mass_quantile_25","stypes",[1])
@filter_none
def _index_mass_quantile(x:list,percentile = 0.25):
    quantile_value = sum(x)*percentile
    xlen = len(x)
    cumsum = 0;
    sign_flag = (quantile_value>=0)
    for i,xval in enumerate(x):
        cumsum+=xval
        if (sign_flag and cumsum>quantile_value) or ((not sign_flag) and cumsum<quantile_value):
            return i/xlen
    return 0

@set_property("name","ndex_mass_quantile_50","stypes",[1])
@filter_none
def _idnex_mass_quantile_50(x):
    return _index_mass_quantile(x,0.5)

@set_property("name","ndex_mass_quantile_75","stypes",[1])
@filter_none
def _idnex_mass_quantile_75(x):
    return _index_mass_quantile(x,0.75)

@set_property("name","categorical_max_freq_key_hash_code", "stypes", [2])
@listify_type
@filter_none
def _categorical_max_freq_key_hash_code(x:list):
    x_freq_count = _appearance_count(x)
    x_max_freq_key = [xkey for xkey,xval in x_freq_count.items() if xval == max(x_freq_count.values())][0]
    # x_freq_count_sort = sorted(x_freq_count.items(), key=lambda d: d[1],reverse=True)
    # x_max_freq_keyax_freq_key = x_freq_count_sort[0][0]
    return _token_hash(x_max_freq_key)

@set_property("name","categorical_min_freq_key_hash_code", "stypes", [2])
@listify_type
@filter_none
def _categorical_min_freq_key_hash_code(x:list):
    x_freq_count = _appearance_count(x)
    x_min_freq_key = [xkey for xkey,xval in x_freq_count.items() if xval == max(x_freq_count.values())][0]
    return _token_hash(x_min_freq_key)

@set_property("name","none_rate", "stypes",[0,1,2])
@listify_type
def _none_rate(x:list):
    return len([a for a in x if a is not None])/len(x)
