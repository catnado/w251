import paho.mqtt.client as mqtt

# connect to broker
broker = "192.168.1.153"
port = 1883
topic = "face"

remote_broker = "169.47.30.186"
remote_port = 1883
remote_topic = "face"

def on_connect_local(client, userdata, flags, rc):
    print("Forwarder connected to local broker with rc: " + str(rc))
    client.subscribe(topic)

def on_connect_remote(client, userdata, flags, rc):
    print("Forwarder connected to remote broker with rc: " + str(rc))

def on_message(client, userdata, msg):
    remote_client.publish(remote_topic, payload=msg.payload, qos=0, retain=False)

def on_publish_remote(client, userdata, result):
    print("Data published to remote broker")

client = mqtt.Client()
client.on_connect = on_connect_local
client.connect(broker, port, 60)
client.on_message = on_message

remote_client = mqtt.Client()
remote_client.on_connect = on_connect_remote
remote_client.on_publish = on_publish_remote
remote_client.connect(remote_broker, remote_port, 60)

client.loop_forever()


