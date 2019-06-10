#!/usr/bin/env python
import random
import subprocess
import queue
import asyncio
import websockets
import json
import sys
import logging
import sqlite3

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO, datefmt='%m-%d %H:%M')
proxy = dict() 
agent = dict()
conn = sqlite3.connect('scores.db')
sql = "CREATE TABLE IF NOT EXISTS scores (game STRING PRIMARY KEY, t TIMESTAMP DEFAULT CURRENT_TIMESTAMP, player1 STRING, player1_score INTEGER, player2 STRING, player2_score INTEGER) ;"
c = conn.cursor()
c.execute(sql)
conn.commit()
conn.close()

q = queue.Queue()

async def agentserver(websocket, path):
    global proxy, agent
    score = None
    gameid = None
    try:
        _msg = await websocket.recv()
        msg = json.loads(_msg)
        name = msg['agent_name'] 
        logging.info("INIT: {}".format(msg))
        if msg['cmd'] == "AGENT":
            agent[name] = websocket
            q.put(name)
            if q.qsize() > 1:
                p1 = q.get()
                p2 = q.get()
                if len(sys.argv) > 2 and sys.argv[2] == "game" and p1 != p2 and agent[p1] != None and agent[p2] != None:
                    mapa = random.choice(["mapa1.bmp","mapa2.bmp","qualify1.bmp"])
                    subprocess.Popen("python3 start.py -s NetAgent,{},ws://localhost:{} -o NetAgent,{},ws://localhost:{} --disable-video -m {}".format(p1, sys.argv[1], p2, sys.argv[1], mapa).split())
                if p1 == p2:
                    q.put(p1) #put player back into queue
            while True:
                m = await agent[name].recv()
                logging.debug("AGENT: {}".format(m))
                await proxy[name].send(m)
        elif msg['cmd'] == 'PROXY':
            proxy[name] = websocket
            gameid = msg['gameid']
            if name not in agent or agent[name] == None:
                logging.error("Agent must connect before Proxy")
                proxy[name].send("CLOSE")
                proxy[name].close()
                return
            while True:
                m = await proxy[name].recv()
                logging.debug("PROXY: {}".format(m))

                msg = json.loads(m)
                if msg['cmd'] == 'update':
                    score = msg['points']

                await agent[name].send(m)
    except websockets.exceptions.ConnectionClosed as e:
        if name in proxy.keys() and proxy[name] != None:
            logging.debug("{}(PROXY) : {}".format(name, str(e)))
            proxy[name].close(1001,"Other end closed")
            proxy[name] = None
        if name in agent.keys() and agent[name] != None:
            logging.debug("{}(AGENT) : {}".format(name, str(e)))
            agent[name].send(json.dumps({'cmd':'destroy'}))
            agent[name].close(1001,"Other end closed")
            agent[name] = None
        if score != None and gameid != None:   #we only commit score in one of the sides (else we would insert 2x)
            try:
                conn = sqlite3.connect('scores.db')
                c = conn.cursor()
                c.execute('INSERT INTO scores (game, player1, player1_score, player2, player2_score) VALUES (?,?,?,?,?)', (gameid, score[0][0], score[0][1], score[1][0], score[1][1] ))
                logging.info("GAME<{}>\t{}({}) vs {}({})".format(gameid,score[0][0], score[0][1], score[1][0], score[1][1]))
                conn.commit()
                conn.close()
            except sqlite3.IntegrityError as error:
                pass #ignore since both agents will try to insert the score

if len(sys.argv) < 2:
    print("Usage: python3 {} port_number [game]".format(sys.argv[0]))
    sys.exit(1)
start_server = websockets.serve(agentserver, port=int(sys.argv[1]))

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
