#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
logging.basicConfig()


######################klang #######################
from lang import kparser,setPY,Kexec
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

def getstockinfo(a):
    return Kl.currentdf['name'] + "-" + Kl.currentdf['code']
 

def kloopexec(code):
    code = " kloop \n" + code + "\nendp;"


###################web socket######################
USERS = set()

def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "execute":
                if data.get("loop"):
                    code = kloopexec(data['content'])
                else:
                    code = data['content']
                await kexec(code)
        
    finally:
        await unregister(websocket)

start_server = websockets.serve(counter, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
