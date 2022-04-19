#!/usr/bin/env python

# klang WS server 管理程序 that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from threading import Lock,Thread
logging.basicConfig()

import threading
import sys 

if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 9099


def PrintException():
    import linecache
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

###################web socket######################
# 服务器列表
server_list=[
]
#用户列表
user_list=[]



mutex = Lock ()
mutexsu = Lock () #server and user 操作

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
        self.state = 0 #空闲的

    async def pack_exe(self,exe):
        msg = {
            "type":"K_EXE"
        }
        msg.update(exe)
        data = json.dumps(msg)
        await self.websocket.send(data)

    def pack_cmd(self,cmd):
        msg = {
            "type":"K_CMD"
        }
        msg.update(cmd)
        data = json.dumps(msg)
        self.websocket.send(data)
    
 
    async def parse(self,msg):
        if msg["type"] == K_RET:
            msg["type"] = U_RET
            await self.exe_user.send(msg) #转发给用户

        if msg["type"] == K_DONE:
            mutex.acquire()
            self.state = 0
            self.exe_user = None
            mutex.release()
            
    def list_increase(self):
        mutexsu.acquire()
        server_list.append(self.websocket)
        mutexsu.release()

    def list_decrease(self):
        mutexsu.acquire()
        if self.websocket in server_list:
            server_list.remove(self.websocket)
        mutexsu.release()
#
# 浏览器用户和管理者交互
#
# USER msg type
# U_REG     = "U_REG"   #用户发给管理者，用户上线
# U_UNREG   = "U_UNREG" #用户发给管理者，用户掉线
U_EXE     = "U_EXE"   #用户发给管理者，用户要执行代码
U_CMD     = "U_CMD"   #用户发给管理者，要更新数据
U_RET     = "U_RET"   #服务器发给用户，执行的结果
U_INFO    = "U_INFO"  #服务器发给用户，用户信息和服务器信息

class UserMSG():
    def __init__(self,websocket):
        self.websocket = websocket
    async def pack_info(self,info):
        msg = {
            "type":"U_INFO"
        }
        msg.update(info)
        data = json.dumps(msg)
        self.websocket.send(data)

    async def pack_ret(self,ret):
        msg = {
            "type":"U_RET",
        }
        msg.update(ret)
        data = json.dumps(msg)
        self.websocket.send(data)

    async def parse(self,msg):
        if msg["type"] == U_EXE:
            mutex.acquire()
            ws = find_server()
            if ws is not None: #找到空闲服务器
                ws.handler.exe_user = self.websocket
                msg["type"]=K_EXE
                ws.handler.state = 1                
                await ws.handler.pack_exe(msg)
            else:
                busy_msg = {"type":U_RET,"code":1001,"errmsg":"没有空闲服务服务器请稍后"}
                data = json.dumps(busy_msg)
                await self.websocket.send(data)
            mutex.release()

        if msg["type"] == U_CMD:
            pass

    def list_increase(self):
        mutexsu.acquire()
        user_list.append(self.websocket)
        mutexsu.release()

    def list_decrease(self):
        mutexsu.acquire()
        if self.websocket in user_list:
            user_list.remove(self.websocket)
        mutexsu.release()


async def send_notices():
    server_state = []
    for s in server_list:
        server_state.append(s.handler.state)
    msg = json.dumps({
        "type":U_INFO,
        "servers":server_state,
        "users":len(user_list),
    })
    for user in user_list:
        try:
            await user.send(msg)
        except:
            print("Use send failed remove from list")
            user.handler.list_decrease()

def find_server():
    for w in server_list:
        if w.handler.state == 0:
            return w
    return None


async def listen(websocket, path):

    if (path == "/" or path ==  "/user"):
        print("A new user connect")
        websocket.handler = UserMSG(websocket)
        websocket.handler.list_increase()
    if (path == "/klang"): 
        print("A new server connect")
        websocket.handler = KlangMSG(websocket)
        websocket.handler.list_increase()

    # send msg to all USERS
    await send_notices()

    # 新链接
    try:
        async for data in websocket: 
            print(data)
            msg = json.loads(data)

            await websocket.handler.parse(msg)        
    except Exception as e:
        websocket.handler.list_decrease()
        PrintException()
        print(e)
    finally:
        websocket.handler.list_decrease()

#data = asyncio.wait_for(s.recv(), timeout=10)

start_server = websockets.serve(listen, "0.0.0.0", port)
print("Websocket manager start port:",port)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


