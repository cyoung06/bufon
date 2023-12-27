#! /usr/bin/env python
import paho.mqtt.client as mqtt
import os
import uuid
from test import MyApp
from threading import Thread


qos = 0

# ROLES
DEFEND = "defend"
TERROR = "terror"

class Manager():
    def __init__(self, url, port):
        self.value = uuid.uuid4()
        self.url = url
        self.port = int(port)

        self.client_thread = Thread(target=self.connect)
        self.client_thread.start()

        self.scores = {"terrorist": 0, "defender": 0}

    def on_connect(self, client, userdata, flags, rc):
        global topic
        print("Connected with result code "+str(rc))
        client.subscribe("game/score/defender", qos=qos)
        client.subscribe("game/score/terrorist", qos=qos)

    def on_message(self, client, userdata, msg):
        decoded_msg = msg.payload.decode("utf-8")

        if msg.topic.startswith("game/score"):
            datakey = ""
            if msg.topic == "game/score/defender":
                datakey = "defender"
            elif msg.topic == "game/score/terrorist":
                datakey = "terrorist"
            
            self.scores[datakey] = int(decoded_msg)
            app.setScore(datakey, self.scores[datakey])
        

    

    def connect(self, client):
        self.client = mqtt.Client(client_id="mgr")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.url, self.port, 60)
        self.client.loop_forever()
        # client.update()
    # return client

mgr_user_env = os.getenv("MGR").split(":")
mgmt = Manager(url=mgr_user_env[0], port=mgr_user_env[1])

app = MyApp(False)

app.MainLoop()
