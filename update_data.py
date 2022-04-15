from Klang.Klang import (
    Klang
)
import sys

Kl = Klang()

print(sys.argv[1])

if sys.argv[1] == "updatestockdata":
    Kl.stocklist = Kl.data_engine.init_stock_list(Kl)
    Kl.updatestockdata()
else :
    Kl.updateall()
