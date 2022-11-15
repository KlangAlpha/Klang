import socketio
from threading import Lock
import logging
logging.basicConfig()

import threading
import sys,os

sys.path.append(os.path.expanduser(sys.path[0] + "/../"))

######################klang #######################
from Klang.lang import kparser,setPY,Kexec

from Klang import (Kl,
    OPEN, O,
    HIGH, H,
    LOW, L,
    CLOSE, C,
    VOLUME, V, VOL,
    TURN,T,
    DATETIME,

    WOPEN, WO,
    WHIGH, WH,
    WLOW, WL,
    WCLOSE, WC,
    WVOLUME, WV, WVOL,
    WTURN,WT,
    WDATETIME,

    MOPEN, MO,
    MHIGH, MH,
    MLOW, ML,
    MCLOSE, MC,
    MVOLUME, MV, MVOL,
    MTURN,MT,
    MDATETIME,

    SMA,MA,EMA,WMA,

    SUM,ABS,STD,

    CROSS,
    REF,BARSLAST,BARSCOUNT,BARSLASTFIND,
    MAX,
    MIN,
    EVERY,
    COUNT,
    HHV,
    LLV,
    IF, IIF,
    MACD,APPROX,
    TRANSVERSE)

from Klang.Klang import Klang_init

if len(sys.argv) > 1:
    canUpdate = sys.argv[1]
    if canUpdate == "canUpdate":
        Kl.canUpdate = True

Klang_init()

code = Kl.code
date = Kl.date

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):
    globals()[name]=val


setPY(getpyglobals,setpyglobals)

def getstockinfo(name=0):
    code = Kl.cur_code
    return Kl.stockdict[code]['name'], code,\
            Kl.day_df['hqltsz'].iloc[-1],\
            Kl.stockdict[code]['tdxbk'],\
            Kl.stockdict[code]['tdxgn']

def get_chouma(code=0):
    return Kl.chouma()

def kloopexec(content):
    code = "kloop \n" + content + "\nendp;"
    return code

def updateall(msg):
    print("update",msg)
    t = threading.Thread(target=Kl.updateall)
    t.start()
def downloadall(msg):
    print("download",msg)
    t = threading.Thread(target=Kl.downloadall)
    t.start()

mutex = Lock ()

user_id = ""
p_count = 0 
def PROGRESS(val=1):
    global p_count
    p_count +=1
    if val == 0 or p_count % val != 0:
        return 
    
    name,code,hqltsz,tdxbk,tdxgn = getstockinfo()
    message = {"retcode":"PROGRESS","name":name,"code":code,\
        "value":str(val)}
    message['user_id'] = user_id
    sio.emit("user_ret",message,namespace="/Kserver")

def DISPLAY(value):
    name,code,hqltsz,tdxbk,tdxgn = getstockinfo()
    message = {"retcode":"DISPLAY","name":name,"code":code,\
        "value":str(value),"hqltsz":hqltsz,'tdxbk':tdxbk,'tdxgn':tdxgn}
    message['user_id'] = user_id
    sio.emit("user_ret",message,namespace="/Kserver")

def execute(data):
    global user_id 
    #print(data)
    
    # 1. 判断是否加loop循环之行
    # 2. loop == False, manager 处理循环
    if data.get("loop") is not None and data.get("loop") != False:
        content = kloopexec(data['content'])
    else:
        content = data['content']+"\n"

    # 2. 执行 busy lock 执行锁
    mutex.acquire()
    user_id = data["user_id"]
    for stockcode in data ["stocklist"]:
        content1 = "code('" + stockcode["code"] + "')\n;" + content
        try:
            Kexec(content1)
        except:
            pass
    # unlock
    mutex.release()   #之行完成，解锁，发通知给web用户
    #print('执行完成')

    # 3. 执行完成
    
    sio.emit('exec_done',{"user_id":user_id},namespace="/Kserver")
    user_id = ""

def get_stock_list(data):
    print(data)
    stocklist = Kl.stocklist
    data ["stocklist"]  = stocklist
    return data

sio = socketio.Client()
hostserver = 'http://localhost:9088'
#hostserver = 'https://klang.org.cn:8099'
          
class KserverNamespace(socketio.ClientNamespace):
    def on_connect(self):
        print('connection established',sio.namespaces)

    def on_disconnect(self):
        print("disconnected from server")
        os._exit(1) #由守护进程解决重启问题

    def on_loop_list_event(self,data):
        data =  get_stock_list(data) 
        self.emit("ret_loop_list",data,namespace="/Kserver")

    def on_do_exec(self,data):
        execute(data)
    def on_do_updataall(self,data):
        updateall(data)

    def on_do_downloadall(self,data):
        downloadall(data)

sio.register_namespace(KserverNamespace('/Kserver'))
sio.connect(hostserver,namespaces=["/Kserver"])
sio.wait()
