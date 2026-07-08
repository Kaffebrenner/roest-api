#!/usr/bin/python

import argparse
import json
import os

import requests

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
API_HOST = os.environ.get("API_HOST")

parser = argparse.ArgumentParser(
    prog="get_inventory",
    description="Get the inventory list",
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

customer_id = r.json()["customers"][0]["id"]

try:
    r = requests.get(
        f"{API_HOST}/inventories/?customer={customer_id}&page_size=all",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

print(json.dumps(r.json(), indent=4))
