#! /usr/bin/env python
import paho.mqtt.client as mqtt
import os
import uuid
from test import MyApp
from threading import Thread


qos = 0


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
        self.winSide = None

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("game/score/defender", qos=qos)
        client.subscribe("game/score/terrorist", qos=qos)
        client.subscribe("A/ready", qos=qos)
        client.subscribe("A/press", qos=qos)
        client.subscribe("B/ready", qos=qos)
        client.subscribe("B/press", qos=qos)
        client.subscribe("game/wonSide", qos=qos)

    def on_message(self, client, userdata, msg):
        decoded_msg = msg.payload.decode("utf-8")
        print(f"{msg.topic} says {decoded_msg}")

        if msg.topic.startswith("game/score"):
            datakey = ""
            if msg.topic == "game/score/defender":
                datakey = "defender"
            elif msg.topic == "game/score/terrorist":
                datakey = "terrorist"
            
            self.scores[datakey] = int(decoded_msg)
            app.setScore(datakey, self.scores[datakey])

            client.publish(f"A/score", str(self.scores["defender"]), 0)
            client.publish(f"B/score", str(self.scores["terrorist"]), 0)
        if msg.topic.endswith("/press"):
            datakey = ""
            if msg.topic == "A/press":
                datakey = "defender"
            elif msg.topic == "B/press":
                datakey = "terrorist"
            if decoded_msg == "true" and self.winSide == datakey:
                self.scores[datakey] += 1
                client.publish(f"game/score/{datakey}", str(self.scores[datakey]), 0)
                self.setWinSide(None)
        if msg.topic == "game/winSide":
            self.setWinSide(decoded_msg)
    
    def setWinSide(self, side):
        self.winSide = side

        if side == "defender":
            self.client.publish("A/blink", "true", 0)
        else:
            self.client.publish("A/blink", "false", 0)

        if side == "attacker":
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

mgr_user_env = os.getenv("MGR").split(":")
mgmt = Manager(url=mgr_user_env[0], port=mgr_user_env[1])

app = MyApp(False)

app.MainLoop()
