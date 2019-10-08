import sys
import os
import urllib
import tensorflow.contrib.tensorrt as trt
import tensorflow as tf
import numpy as np
import time
from tf_trt_models.detection import download_detection_model, build_detection_graph
import cv2
import paho.mqtt.client as mqtt

# Download frozen graph
FROZEN_GRAPH_NAME = 'data/frozen_inference_graph_face.pb'
!wget https://github.com/yeephycho/tensorflow-face-detection/blob/master/model/frozen_inference_graph_face.pb?raw=true -O {FROZEN_GRAPH_NAME}

# Load the frozen graph
output_dir=''
frozen_graph = tf.GraphDef()
with open(os.path.join(output_dir, FROZEN_GRAPH_NAME), 'rb') as f:
    frozen_graph.ParseFromString(f.read())

# Constants
INPUT_NAME='image_tensor'
BOXES_NAME='detection_boxes'
CLASSES_NAME='detection_classes'
SCORES_NAME='detection_scores'
MASKS_NAME='detection_masks'
NUM_DETECTIONS_NAME='num_detections'

input_names = [INPUT_NAME]
output_names = [BOXES_NAME, CLASSES_NAME, SCORES_NAME, NUM_DETECTIONS_NAME]

# Optimize the frozen graph using TensorRT
trt_graph = trt.create_inference_graph(
    input_graph_def=frozen_graph,
    outputs=output_names,
    max_batch_size=1,
    max_workspace_size_bytes=1 << 25,
    precision_mode='FP16',
    minimum_segment_size=50
)

# Create session and load graph
tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True
​
tf_sess = tf.Session(config=tf_config)

tf.import_graph_def(frozen_graph, name='')
​
tf_input = tf_sess.graph.get_tensor_by_name(input_names[0] + ':0')
tf_scores = tf_sess.graph.get_tensor_by_name('detection_scores:0')
tf_boxes = tf_sess.graph.get_tensor_by_name('detection_boxes:0')
tf_classes = tf_sess.graph.get_tensor_by_name('detection_classes:0')
tf_num_detections = tf_sess.graph.get_tensor_by_name('num_detections:0')


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
face_cascade = cv2.CascadeClassifier('HW07/haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(1)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    image_resized = np.array(frame.resize((300, 300)))
    image = np.array(image)
    
    # face detection, cropping, and encoding
    scores, boxes, classes, num_detections = tf_sess.run([tf_scores, tf_boxes, tf_classes,\
	tf_num_detections], feed_dict={
    		tf_input: image_resized[None, ...]
	})

    # only take one face..
    box = boxes[0][0]
    score = scores[0][0]
    if score < 0.5:
        continue

    face_crop = image[int(box[0]):int(box[2]), int(box[1]):int(box[3]), :]
    print("face detected")
    retval, buf = cv2.imencode(".png", face_crop)
    face_binary = buf.tobytes()
        
    # publish
    client.publish(topic, payload=face_binary, qos=0, retain=False)




