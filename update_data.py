from Klang.Klang import (
    Kl,Klang_init
)
import sys

Kl.canUpdate = True

if len(sys.argv) > 1:
    Kl.downloadall()
else:
    Klang_init()
    Kl.updateall()

