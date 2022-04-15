from Klang.Klang import (
    Klang
)
import sys

Kl = Klang()

print(sys.argv[1])

Kl.stocklist = Kl.data_engine.init_stock_list(Kl)

if len(sys.argv)> 0 and sys.argv[1] == "updatestockdata":
    Kl.updatestockdata()
else :
    Kl.updateall()
