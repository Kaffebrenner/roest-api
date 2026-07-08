#!/usr/bin/python

import argparse
import json
import os
import time
from pathlib import Path

import requests

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
API_HOST = os.environ.get("API_HOST")
EXPORT_DIR = "export"

parser = argparse.ArgumentParser(
    prog="export_logs",
    description="Export logs from for a given machine",
)
parser.add_argument("machine_slug")
parser.add_argument(
    "number_of_logs",
    nargs="?",
    type=int,
    default=10,
    help="Number of logs to export, starting from the most recent log. Default: 10",
)
args = parser.parse_args()

print(f"API_HOST: {API_HOST}")

Path(f"{EXPORT_DIR}/{args.machine_slug}").mkdir(parents=True, exist_ok=True)

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

machine_id = r.json()[0]["id"]

try:
    r = requests.get(
        f"{API_HOST}/logs/?machine={machine_id}&page_size={args.number_of_logs}",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

results = r.json()["results"]
log_ids = [(log["id"], log["batch_no"]) for log in results]

with open(f"{EXPORT_DIR}/{args.machine_slug}.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(results, indent=4))

for log_id, batch_no in log_ids:
    tries = 3
    while tries > 0:
        try:
            r = requests.get(
                f"{API_HOST}/datapoints/?log={log_id}&page_size=all",
                headers=headers,
                timeout=10,
            )
            r.raise_for_status()
            break
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 429:
                delay = int(err.response.headers.get("Retry-After", 30))
                print(f"{err.response.text}, retrying in {delay} seconds...")
                time.sleep(delay)
                tries -= 1
                if tries > 0:
                    continue
            print(err.response.text)
            raise SystemExit(err) from err

    with open(
        f"{EXPORT_DIR}/{args.machine_slug}/{batch_no}.json", "w", encoding="utf-8"
    ) as f:
        f.write(json.dumps(r.json(), indent=4))
