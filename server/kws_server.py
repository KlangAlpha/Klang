#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from threading import Lock
logging.basicConfig()

import threading
import sys,os 

#sys.path.append(os.path.expanduser("~") + "/Klang")

######################klang #######################
from Klang.lang import kparser,setPY,Kexec

from Klang import (Kl,
    OPEN, O,
    HIGH, H,
    LOW, L,
    CLOSE, C,
    VOLUME, V, VOL,
    DATETIME,

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
    MACD,APPROX)

from Klang.Klang import Klang_init

Klang_init()

code = Kl.code
date = Kl.date

ws = None

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):
    globals()[name]=val


setPY(getpyglobals,setpyglobals)

def getstockinfo(name=0):
    return Kl.currentdf['name'], Kl.currentdf['code'],\
            Kl.currentdf['df']['hqltsz'].iloc[-1],\
            Kl.currentdf['tdxbk'],\
            Kl.currentdf['tdxgn']
 
def get_chouma(code=0):
    return Kl.chouma()

def kloopexec(content):
    code = "kloop \n" + content + "\nendp;"
    return code

def updateall(msg):
    #pw   = msg['pw']
    print("update",msg)
    t = threading.Thread(target=Kl.updateall)
    t.start()
###################web socket######################
mutex = Lock ()

def await_run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

# 因为DISPLAY是需要在Klang执行，所以需要await_run执行 sync消息
def DISPLAY(value):
    name,code,hqltsz,tdxbk,tdxgn = getstockinfo()
    chouma = Kl.chouma()
    message = {"type":K_RET,"name":name,"code":code,\
        "value":str(value),"hqltsz":hqltsz,'tdxbk':tdxbk,'tdxgn':tdxgn,'chouma':chouma}
    msg = json.dumps(message)
    await_run(ws.send(msg))

async def execute(handler,data):
    print(data)

    # 1. 判断是否加loop循环之行
    if data.get("loop") is not None:
        code = kloopexec(data['content'])
    else:
        code = data['content']+"\n"

    # 2. 执行 busy lock 执行锁
    mutex.acquire()

    Kexec(code)
    # unlock

    mutex.release()   #之行完成，解锁，发通知给web用户
    print('执行完成')

    # 3. 执行完成 
    await handler.done()

# server 和klang执行服务器交互
# Klang msg type
#K_REG          = "K_REG"   #服务器发送给管理这服务器上线
#K_UNREG        = "K_UNREG" #服务器发送给管理者服务器离开
K_HEARTBEAT    = "K_HEART" #心跳包 
K_EXE          = "K_EXE"  #管理者发送给服务器
K_DONE         = "K_DONE" #服务器返回给管理者
K_CMD          = "K_CMD"  #管理者发送给服务器
K_RET          = "K_RET"  #服务器返回给管理者

class KlangMSG():
    def __init__(self,websocket):
        self.websocket = websocket

    def pack_exe(self,exe):
        msg = {
            "type":"K_EXE"
        }
        msg.update(exe)
        data = json.dumps(msg)
        self.websocket.send(data)

    def pack_cmd(self,cmd):
        msg = {
            "type":"K_CMD"
        }
        msg.update(cmd)
        data = json.dumps(msg)
        self.websocket.send(data)
    
 
    async def parse(self,msg):
        if msg["type"] == K_EXE:
            await execute(self,msg)    
        if msg["type"] == K_DONE:
            mutex.acquire()
            self.state = 0
            self.exe_user = None
            mutex.release()
        if msg["type"] == K_CMD:
            if msg["content"] == "UPDATEALL":
                updateall(msg)

    async def done(self):
        msg ={"type":K_DONE}
        data = json.dumps(msg)
        await self.websocket.send(data)

#klang server
#server_host = 'ws://localhost:9088/klang'
server_host = 'wss://klang.org.cn:8099/klang'
server_host = 'ws://klang.org.cn:9099/klang'

async def conn_server():

    global ws #for DISPALY

    while True:
        try:
            async with websockets.connect(server_host) as websocket:
                print("connect success!",server_host)
                websocket.handler = KlangMSG(websocket)
                ws = websocket

                while True:
                    data = await websocket.recv()
                    msg = json.loads(data)
                    await websocket.handler.parse(msg)

        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                break

        print("connect server error,try again ",server_host)
        await asyncio.sleep(2)

asyncio.get_event_loop().run_until_complete(conn_server())

