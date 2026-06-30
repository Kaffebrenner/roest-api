#!/usr/bin/python

import argparse
import os
from enum import IntEnum

import requests

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
API_HOST = os.environ.get("API_HOST")
CONNECT_HOST = os.environ.get("CONNECT_HOST")

parser = argparse.ArgumentParser(
    prog="create_profile",
    description="Create a new profile",
)
args = parser.parse_args()

print(f"API_HOST: {API_HOST}")

try:
    r = requests.post(
        f"{API_HOST}/o/token/",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "read write",
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
        f"{API_HOST}/users/self/",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

customer = r.json()["customers"][0]["url"]


class MachineType(IntEnum):
    S100L100 = 0
    P3000 = 1
    S200L200 = 2


class ProfileType(IntEnum):
    AIR_TEMP = 0
    BEAN_TEMP = 1
    POWER = 2
    INLET_TEMP = 5
    POWER_BT = 6
    INLET_BT = 7


class EndCondition(IntEnum):
    NONE = 0
    TOTAL_TIME = 1
    DEV_TIME = 2
    DTR = 3
    BEAN_TEMP = 4
    DRUM_TEMP = 5


try:
    r = requests.post(
        f"{API_HOST}/profiles/",
        headers=headers,
        json={
            "name": "name of the profile",
            "notes": "profile description goes here",
            "machinetype": MachineType.S100L100,
            "profile_type": ProfileType.INLET_TEMP,
            "temperature_bezier": [[0, 250], [360000, 250]],
            "power_bezier": None,
            "rpm_bezier": [[0, 55], [360000, 55]],
            "fan_bezier": [[0, 75], [360000, 75]],
            "batch_weight": 100,
            "preheat_temperature": 180,
            "end_condition": EndCondition.TOTAL_TIME,
            "end_condition_value": 6 * 60 * 1000,
            "reversed_drum_direction": False,
            "is_bbp_profile": False,
            "customer": customer,
        },
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

returned_json = r.json()
profile_id = returned_json["id"]
print(returned_json)
print(f"Created profile with id {profile_id}")

try:
    r = requests.patch(
        f"{API_HOST}/profiles/{profile_id}/",
        headers=headers,
        json={
            "temperature_bezier": [[0, 240], [360000, 270]],
            "end_condition": EndCondition.TOTAL_TIME,
            "end_condition_value": 5.5 * 60 * 1000,
        },
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

returned_json = r.json()
profile_id = returned_json["id"]
print(returned_json)
print(f"Updated profile with id {profile_id}")

try:
    r = requests.put(
        f"{API_HOST}/profiles/{profile_id}/enable_share/",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

returned_json = r.json()
profile_uuid = returned_json["share_uuid"]
share_url = f"{CONNECT_HOST}/shared_profile/{profile_uuid}/"
print(f"Shared profile available at {share_url}")
