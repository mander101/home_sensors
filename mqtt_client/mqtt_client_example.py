import random
import time
import threading
import paho.mqtt.client as mqtt

# Define the MQTT broker details
broker = '192.168.1.241'
port = 1883  # typically 1883 for non-secure connections, 8883 for secure
topic = 'test'
client_id = 'your_client_id'
username = "vanpye00"
password = "1264easterlane"

# The callback for when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connection failed with code ", rc)

# The callback for when a PUBLISH message is sent to the server
def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")

# Create an MQTT client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)

# Set username and password
client.username_pw_set(username, password)

# Assign the on_connect and on_publish callback functions


# Connect to the broker
client.connect(broker, port, keepalive=60)

# Start the network loop
client.loop_start()

# Publish a message
message = "Hello MQTT"
result = client.publish(topic, message)

# Wait for the message to be published
result.wait_for_publish()

# Stop the network loop and disconnect
client.loop_stop()
client.disconnect()
