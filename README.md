# ROEST API

This provides an incomplete and potentially incorrect description of the ROEST
API. It is intended to provide a starting point for custom integration with
the API.

The API does not provide any guarantees about stability and will break
backwards compatibility.

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## Obtain credentials

Create the .env file

    cp env.example .env

Create API credentials at https://connect.roestcoffee.com/settings/api and
store them in the .env file.

## Run example code

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

    ./run.sh get_inventory.py

    ./run.sh set_weight.py p3000-rXX-YY 2700

    ./run.sh live_data.py p3000-rXX-YY

    ./run.sh create_profile.py

    ./run.sh export_logs.py p3000-rXX-YY


## View OpenAPI schema

Start a swagger server that serves the specification documentation:

    docker run -p 8080:8080 -e SWAGGER_JSON=/schema.yml -v ${PWD}/schema.yml:/schema.yml swaggerapi/swagger-ui

Open http://localhost:8080 in a browser.
