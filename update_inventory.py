#!/usr/bin/python

import argparse
import os
import sys

import requests

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
API_HOST = os.environ.get("API_HOST")

parser = argparse.ArgumentParser(
    prog="update_inventory",
    description="Update the weight for a specific inventory item",
)
parser.add_argument("search_term", help="Search term to identify the inventory item")
parser.add_argument("current_weight", type=float, help="The new weight in grams")
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

customer_id = r.json()["customers"][0]["id"]

try:
    r = requests.get(
        f"{API_HOST}/inventories/?customer={customer_id}&is_archived=false&search={args.search_term}",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

results = r.json()["results"]
count = len(results)

if count == 0:
    print(f"No inventory item found for '{args.search_term}'")
    sys.exit(1)
elif count > 1:
    print(
        f"Multiple inventory items found for '{args.search_term}'. Please be more specific."
    )
    for item in results:
        print(f" - {item['name']}")
    sys.exit(1)

inventory_item = results[0]
inventory_id = inventory_item["id"]
inventory_name = inventory_item.get("name", "Unknown")

try:
    r = requests.patch(
        f"{API_HOST}/inventories/{inventory_id}/",
        headers=headers,
        json={
            "current_weight": args.current_weight,
        },
        timeout=10,
    )
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err.response.text)
    raise SystemExit(err) from err

updated_item = r.json()
print(f"Updated '{inventory_name}' weight to {updated_item['current_weight']}g")
