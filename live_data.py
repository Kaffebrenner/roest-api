#!/usr/bin/python

import argparse
import json
import os

import paho.mqtt.client as mqtt
import requests

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
API_HOST = os.environ.get("API_HOST")
MQTT_HOST = os.environ.get("MQTT_HOST", "coap.roestcoffee.com")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 8883))

parser = argparse.ArgumentParser(
    prog="live_data",
    description="Get live data for a machine",
)
parser.add_argument("machine_slug")
args = parser.parse_args()

print(f"API_HOST: {API_HOST}")

try:
    r = requests.post(
        f"{API_HOST}/o/token/",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

access_token = r.json()["access_token"]
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json; version=1.0",
}

try:
    r = requests.get(
        f"{API_HOST}/machines/?slug={args.machine_slug}&page_size=all",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

machine = r.json()[0]
machine_id = machine["id"]

sensor_config = machine["sensor_config"]
has_inlet = sensor_config["has_inlet"]
has_drum = sensor_config["has_drum"]

mqtt_config = machine["mqtt_config"]
mqtt_user = mqtt_config["username"]
mqtt_pass = mqtt_config["subscribe_password"]
mqtt_topic = mqtt_config["topic"]


def on_connect_handler(_client, _userdata, _flags, status, _properties):
    if status == 0:
        print(f"Connected with status code: {status}")
        res = client.subscribe(mqtt_topic)
        print("subscribe res:", res)
    else:
        print("connection failed:", status)


def on_subscribe_handler(_client, _userdata, mid, granted_qos, _properties):
    print(f"Subscribe status: {mid}, granted_qos: {granted_qos}")
    if granted_qos[0] != 128:
        print("Subscription established")
    else:
        print("Could not subscribe to topic: {mqtt_topic}, qos: {granted_qos[0]}")


def on_message_handler(_client, _userdata, msg):
    d = json.loads(msg.payload)["data"]
    print(
        f"{d["msec"] // 1000}: bt:{d["bt"]} "
        f"inlet:{d["inlet_temp"] if has_inlet else "N/A"} "
        f"drum:{d["drum_temp"] if has_drum else "N/A"}"
    )


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    clean_session=True,
    reconnect_on_failure=True,
)
if MQTT_PORT == 8883:
    client.tls_set()

client.username_pw_set(mqtt_user, mqtt_pass)

client.on_connect = on_connect_handler
client.on_subscribe = on_subscribe_handler
client.on_message = on_message_handler

client.connect(host=MQTT_HOST, port=MQTT_PORT)
client.loop_forever()
