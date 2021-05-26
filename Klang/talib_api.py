#
# Ta-lib
#

import talib

def MA(X,N):
    return talib.MA(X.data,N)
