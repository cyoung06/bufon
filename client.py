#! /usr/bin/env python
import paho.mqtt.client as mqtt
import os
import uuid
from threading import Thread
import http.server
import socketserver
from typing import Tuple
import json
from http import HTTPStatus
import subprocess
import vlc
import time
from test import MyApp


qos = 0

criticalPoint = 3


class Manager():
    def __init__(self, url, port):
        print("INIT MGR")
        self.value = uuid.uuid4()
        self.url = url
        self.port = int(port)

        print("Start thread!")
        self.client_thread = Thread(target=self.connect)
        self.client_thread.start()

        self.scores = {"terrorist": 0, "defender": 0}
        self.winSide = "none"
        self.played = False
        self.playingProcess = None

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("game/score/defender", qos=qos)
        client.subscribe("game/score/terrorist", qos=qos)
        client.subscribe("A/ready", qos=qos)
        client.subscribe("A/press", qos=qos)
        client.subscribe("B/ready", qos=qos)
        client.subscribe("B/press", qos=qos)
        client.subscribe("game/winSide", qos=qos)

    def playRound(self):
        if self.playingProcess is not None:
            self.playingProcess.terminate()
            self.playingProcess = None
        
        os.system(f"/usr/bin/aplay sounds/start.wav")
        self.playingProcess = subprocess.Popen([f'/usr/bin/aplay', f'sounds/r{self.scores["terrorist"] + self.scores["defender"] + 1}.wav'])
    def stopRound(self):
        if self.playingProcess is not None:
            self.playingProcess.terminate()
            self.playingProcess = None


    def on_message(self, client, userdata, msg):
        decoded_msg = msg.payload.decode("utf-8")
        # print(f"{msg.topic} says {decoded_msg}")

        if msg.topic.startswith("game/score"):
            datakey = ""
            if msg.topic == "game/score/defender":
                datakey = "defender"
            elif msg.topic == "game/score/terrorist":
                datakey = "terrorist"
            isIncrease = int(decoded_msg) - self.scores[datakey] > 0
            self.scores[datakey] = int(decoded_msg)
            app.setScore(datakey, self.scores[datakey])

            if self.playingProcess is not None:
                self.playingProcess.terminate()
                self.playingProcess = None
            

            if self.scores["terrorist"] + self.scores["defender"] >= criticalPoint:
                isLeftWin = self.scores["defender"] > self.scores["terrorist"]
                self.scores["defender"] = 0
                self.scores["terrorist"] = 0
                if not self.played:
                    self.played = True
                    os.system(f"/usr/bin/aplay sounds/round_{datakey}.wav") 
                    os.system(f"/usr/bin/aplay sounds/victory_{'defender' if isLeftWin else 'terrorist'}.wav")
                    time.sleep(1)
                    # app.endGame(isLeftWin)
                    # subprocess.Popen(["python", "vlctest.py", ""])
                    
                    os.system(f"./hax.sh videos/{'defend2.mp4' if isLeftWin else 'terror2.mp4' }")
                    self.played = False
                    client.publish(f"game/score/defender", 0, 0)
                    client.publish(f"game/score/terrorist", 0, 0)
            elif isIncrease:
                os.system(f"/usr/bin/aplay sounds/round_{datakey}.wav") 
                
        if msg.topic.endswith("/press"):
            datakey = ""
            if msg.topic == "A/press":
                datakey = "defender"
            elif msg.topic == "B/press":
                datakey = "terrorist"
            if decoded_msg == "true" and self.winSide == datakey:
                self.setWinSide("none")
                self.client.publish(f"game/score/{datakey}", str(self.scores[datakey] + 1), 0)

                

        if msg.topic == "game/winSide":
            self.setWinSide(decoded_msg)
    
    def modifyScore(self, side, delta):
        self.client.publish(f"game/score/{side}", str(self.scores[side] + delta), 0)

    def setWinSide(self, side):
        if self.winSide != side:
            self.client.publish("game/winSide", side, 0)
        self.winSide = side
        self.client.publish(f"A/score", str(self.scores["defender"]), 0)
        self.client.publish(f"B/score", str(self.scores["terrorist"]), 0)

        if side == "defender":
            self.client.publish("A/blink", "true", 0)
        else:
            self.client.publish("A/blink", "false", 0)

        if side == "terrorist":
            self.client.publish("B/blink", "true", 0)
        else:
            self.client.publish("B/blink", "false", 0)
    

    def connect(self):
        print("awesome connecting")
        self.client = mqtt.Client(client_id="mgr")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print(f"Connecting to... {self.url} {self.port}")
        self.client.connect(self.url, self.port, 60)
        print("Conntected! looping!")
        self.client.loop_forever()
        # client.update()
    # return client

class Handler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        super().__init__(request, client_address, server)

    @property
    def api_response(self):
        return json.dumps({"score": mgmt.scores, "winSide": mgmt.winSide }).encode()

    def do_GET(self):
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(self.api_response))
        elif self.path.startswith('/winSide'):
            if mgmt.playingProcess is not None:
                if (self.path == '/winSide/defender'):
                    mgmt.setWinSide('defender')
                elif (self.path == '/winSide/terrorist'):
                    mgmt.setWinSide('terrorist')
                elif (self.path == '/winSide/none'):
                    mgmt.setWinSide("none")
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
        elif self.path == '/terrorist/inc':
            mgmt.modifyScore('terrorist', 1)
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
        elif self.path == '/terrorist/dec':
            mgmt.modifyScore('terrorist', -1)
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
        elif self.path == '/defender/inc':
            mgmt.modifyScore('defender', 1)
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
        elif self.path == '/defender/dec':
            mgmt.modifyScore('defender', -1)
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
        elif self.path == '/startround':
            mgmt.playRound()
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()    
        elif self.path == '/stopround':
            mgmt.stopRound()
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()    

def runtcp():
    my_server = socketserver.TCPServer(("0.0.0.0", 8080), Handler)
    my_server.serve_forever()


if __name__ == "__main__":
    mgr_user_env = os.getenv("MGR").split(":")
    mgmt = Manager(url=mgr_user_env[0], port=mgr_user_env[1])

    Thread(target=runtcp).start()

    app = MyApp(False)
    app.MainLoop()