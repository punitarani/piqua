# Read config.json file

import json
from defs import CONFIG_JSON


# Read config.json file
with open(CONFIG_JSON) as cfg:
    config_data = json.load(cfg)


# First Level
host: str = config_data.get("host")
tda_data: dict = config_data.get("tda")

# Second Level
# TDA
account_id: str = tda_data.get("account_id")
client_id: str = tda_data.get("client_id")
redirect_uri: str = tda_data.get("redirect_url")


if __name__ == "__main__":
    print(host, tda_data)
