#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from threading import Lock
logging.basicConfig()


######################klang #######################
from Klang.lang import kparser,setPY,Kexec
from Klang.common import today
from Klang import Kl,C,MA,CROSS

#
# today 
#

def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):
    globals()[name]=val


setPY(getpyglobals,setpyglobals)

def getstockinfo():
    return Kl.currentdf['name'], Kl.currentdf['code']
 

def kloopexec(webindex,content):
    code = "webindex =" + str(webindex) + "\n"
    code += "kloop \n" + content + "\nendp;"
    return code

def cmd_call(code):
    if code == "reset_list":
        pass
    if code == "reload_stock":
        pass

###################web socket######################
USERS = {}
index = 0
busy = 0
mutex = Lock ()

def await_run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value

def DISPLAY(webindex,value):
    name,code = getstockinfo()
    message = {"type":"display","name":name,"code":code,"value":value}
    msg = json.dumps(message)
    await_run(USERS[webindex].send(msg))

def users_event():
    return json.dumps({"type": "users", "count": len(USERS),"busy":busy})


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([USERS[user].send(message) for user in USERS])

async def notice(message):
    msg = json.dumps(message)
    await asyncio.wait([USERS[user].send(msg) for user in USERS])

async def register(websocket):
    global USERS,index
    USERS[index] = websocket
    index += 1 
    await notify_users()
    return index - 1

async def unregister(index):
    del USERS[index]
    await notify_users()


async def counter(websocket, path):
    global busy
    # register(websocket) sends user_event() to websocket
    webindex = await register(websocket) #webindex is fixed name,use by *.html
    print("register ",webindex,USERS)
    try:
        async for message in websocket:
            data = json.loads(message)
            print(data)
            if data["action"] == "execute":
                if busy == 1:
                    await notice({"type":"busy","value":True,"op" :False})
                    continue
                if data.get("loop") is not None:
                    code = kloopexec(webindex,data['content'])
                else:
                    code = "webindex="+str(webindex)+"\n" + data['content']+"\n"

                # busy lock
                mutex.acquire()
                busy = 1
                await notice({"type":"busy","value":True})

                Kexec(code)

                # unlock
                mutex.release()   
                await notice({"type":"busy","value":False})
                busy = 0

            if data["action"] == "cmd":
                    code = data['content']
                    cmd_call(code)     
    finally:
        await unregister(webindex)

start_server = websockets.serve(counter, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
