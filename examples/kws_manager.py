#!/usr/bin/env python

# klang WS server 管理程序 that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from threading import Lock
logging.basicConfig()

import threading
import sys 

if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 9099

###################web socket######################
# 服务器列表
server_list=[
    (127.0.0.1,9091),    
]
#服务器和用户对应表
server_user={

}

#用户列表
USERS = {}

#msg format
msg = {
    "type"    :"",
    "content" :{
        "value": "",
    },
}

# server 和klang执行服务器交互
# Klang msg type
K_REG     = "K_REG"
K_UNREG   = "K_UNREG"
K_LIVE    = "K_LIVE"
K_EXE     = "K_EXE"
K_DONE    = "K_DONE"
K_CMD     = "K_CMD"
K_RET     = "K_RET"

class KlangMSG():
    def __init__(self):
        pass
    def pack(self):
        pass
    def unpack(self):
        pass
    def recv(self):
        pass
    def send(self):
        pass
#
# 浏览器用户和server交互
#
# USER msg type
U_REG     = "U_REG"
U_UNREG   = "U_UNREG"
U_LIVE    = "U_LIVE"
U_EXE     = "U_EXE"
U_CMD     = "U_CMD"
U_RET     = "U_RET"

class UserMSG():
    def __init__(self):
        pass
    def pack(self):
        pass
    def unpack(self):
        pass
    def recv(self):
        pass
    def send(self):
        pass

index = 0
busy  = 0
mutex = Lock ()
current = 0 # default display user

def await_run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

# 因为DISPLAY是需要在Klang执行，所以需要await_run执行 sync消息
def DISPLAY(value):
    name,code,hqltsz,tdxbk,tdxgn = getstockinfo()
    chouma = Kl.chouma()
    message = {"type":"display","name":name,"code":code,\
        "value":str(value),"hqltsz":hqltsz,'tdxbk':tdxbk,'tdxgn':tdxgn,'chouma':chouma}
    msg = json.dumps(message)
    await_run(USERS[current].send(msg))

def users_event():
    return json.dumps({"type": "users", "count": len(USERS),"busy":busy})


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([USERS[user].send(message) for user in USERS])

async def notice(message):
    msg = json.dumps(message)
    await asyncio.wait([USERS[user].send(msg) for user in USERS])

mutexuser = Lock ()

async def register(websocket):
    global USERS,index
    mutexuser.acquire()
    USERS[index] = websocket
    index += 1 
    mutexuser.release()
    await notify_users()
    return index - 1

async def unregister(index):
    mutexuser.acquire()
    if USERS.get(index,None) != None:
        del USERS[index]
    mutexuser.release()
    await notify_users()


async def execute(data,webindex):
    global busy,current
    print(data)
    # 1. 判断是否在执行中
    if busy == 1: #同时只能有一人之行
        await notice({"type":"busy","value":True,"op" :False})
        return

    # 2. 判断是否加loop循环之行
    if data.get("loop") is not None:
        code = kloopexec(webindex,data['content'])
    else:
        code = "webindex="+str(webindex)+"\n" + data['content']+"\n"

    # 3. 执行 busy lock 执行锁
    mutex.acquire()

    current = webindex
    busy = 1
    await notice({"type":"busy","value":True})
    Kexec(code)
    # unlock

    mutex.release()   #之行完成，解锁，发通知给web用户
    print('执行完成')

    # 4. 执行完成 
    await notice({"type":"busy","value":False})
    current = 0
    busy = 0



async def listen(websocket, path):

    if (path == "/" or path ==  "/user"):
        websocket.handler = UserMSG()
    if (path == "/klang"): 
        websocket.handler = KlangMSG()
    # 新链接
    while 1:
        name = await websocket.recv()
        websocket.handler.print(f"< {name}")

        greeting = f"Hello {name}!"

        await websocket.send(greeting)
        websocket.handler.print(f"> {greeting}")
    webindex = await register(websocket) #webindex is fixed name,use by *.html

    print("register ",webindex,USERS)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "execute":
                await execute(data,webindex)

            if data["action"] == "cmd":
                cmd_call(data)     
    except:
        if current == webindex:
            current = 0
            busy = 0
        await unregister(webindex)
    finally:
        await unregister(webindex)
        
start_server = websockets.serve(listen, "0.0.0.0", port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


#klang server
import asyncio
import websockets
server_host = 'ws://localhost:9099/klang'
#server_host = 'wss://klang.org.cn:8099/klang'

async def conn_server():
    while True:
        try:
            async with websockets.connect(server_host) as websocket:
                print("connect success!",server_host)
                while True:
                    msg = await websocket.recv()
                    await websocket.send('msg')
        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                break
   
        print("connect server error,try again ",server_host)
        await asyncio.sleep(2)

asyncio.get_event_loop().run_until_complete(conn_server())