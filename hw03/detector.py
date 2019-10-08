import numpy as np
import cv2
import paho.mqtt.client as mqtt


# connect to broker
# host = "192.168.1.153"
host = "169.47.30.186"
port = 1883
topic = "face"

def on_connect(client, userdata, flags, rc):
    print("Detector connected to local broker with rc: " + str(rc))

def on_publish(client, userdata, result):
    print("Data published to local broker")

client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.connect(host, port, 60)

# detect, capture, and publish face
face_cascade = cv2.CascadeClassifier('HW03/haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(1)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # We don't use the color information, so might as well save space
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # face detection, cropping, and encoding
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        face_crop = frame[y:y+h,x:x+w]
        print("face detected")
        retval, buf = cv2.imencode(".png", face_crop)
        face_binary = buf.tobytes()
        
        # publish
        client.publish(topic, payload=face_binary, qos=0, retain=False)
        




