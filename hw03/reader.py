import numpy as np
import cv2
import math
import paho.mqtt.client as mqtt

image_number = 0

broker = "169.47.30.186"
port = 1883
topic = "face"

def on_connect(client, userdata, flags, rc):
   print("Connected with rc: " + str(rc))
   client.subscribe(topic)

def on_message(client, userdata, msg):
   global image_number
   f = np.frombuffer(msg.payload, dtype='uint8')
   img = cv2.imdecode(f, flags=1)
   print("face received")
   img_name = "/HW03/face-" + str(image_number) + ".png"
   image_number += 1
   cv2.imwrite(img_name, img)

client = mqtt.Client()
client.on_connect = on_connect
client.connect(broker, port, 60)
client.on_message = on_message
client.loop_forever()