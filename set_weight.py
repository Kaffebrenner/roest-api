#!/usr/bin/python

import argparse
import os
from enum import IntEnum

import requests

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
API_HOST = os.environ.get("API_HOST")

parser = argparse.ArgumentParser(
    prog="set_weight",
    description="Set the end weight for the most recent log for a machine",
)
parser.add_argument("machine_slug")
parser.add_argument("end_weight", type=int)
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
        f"{API_HOST}/machines/?slug={args.machine_slug}&page_size=all",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

machine_id = r.json()[0]["id"]


class EventFlags(IntEnum):
    CHARGE = 1 << 1
    DROP = 1 << 2
    FIRSTCRACK = 1 << 3
    DRYEND = 1 << 5
    MANUAL = 1 << 6


try:
    r = requests.get(
        f"{API_HOST}/logs/?event_flags={EventFlags.DROP}&machine={machine_id}&page_size=3",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

log_id = r.json()["results"][0]["id"]
start_weight = r.json()["results"][0]["start_weight"]

try:
    r = requests.post(
        f"{API_HOST}/logs/{log_id}/weights/",
        headers=headers,
        json={
            "start_weight": start_weight,
            "end_weight": args.end_weight,
        },
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

returned_json = r.json()
batch_no = returned_json["batch_no"]
end_weight = returned_json["end_weight"]

print(f"New end weight for log #{batch_no}: {end_weight}")
