import json

from defs import CONFIG_JSON
from src.loggers import SystemLogger

logger = SystemLogger("main").logger


# Create Config.json template
def create_configJson(overwrite: bool = False, take_input: bool = False):
    logger.info("Creating config.json file.")

    config_data = {
        "host": "local",
        "tda": {
            "account_id": "",
            "client_id": "",
            "redirect_url": "https://localhost"
        }
    }

    # Read config.json file
    try:
        with open(CONFIG_JSON, "r") as cfg:
            data = json.load(cfg)
    except json.JSONDecodeError:
        logger.info("Could not read existing config.json file.")
        data = {}

    # Write data to config.json
    if data == {} or overwrite:

        # Update config data with user inputs
        if take_input:
            print("Input config data.\n"
                  "Leave blank to use default values.\n")

            # Host
            host = input("Host (local or remote): ").lower()
            if host == "":
                host = "local"
                print("Using default: {}".format(host))

            while host not in ["local", "remote"]:
                host = input("Please enter valid host type: ").lower()

            # TDA Account ID
            tda_account_id = input("Enter TD Ameritrade Account ID: ")

            # TDA Client ID
            tda_client_id = input("Enter TDA API Client ID: ")

            # TDA Redirect URL
            tda_redirect_url = input("Enter TDA API Redirect URL: ").lower()
            if tda_redirect_url == "":
                tda_redirect_url = "https://localhost"
                print("Using default: {}".format(tda_redirect_url))

            while tda_redirect_url[:4] != "http":
                tda_redirect_url = input("Please enter valid Redirect URL (http/https://...): ").lower()

            # Update config_data dict with user inputted values
            config_data.update({"host": host})

            config_data.get("tda").update({"account_id": tda_account_id,
                                           "client_id": tda_client_id,
                                           "redirect_url": tda_redirect_url})

        # Write config_data to config.json file
        with open(CONFIG_JSON, "w") as cfg:
            json.dump(config_data, fp=cfg)

        # Log
        if data == {}:
            logger.info("Created config.json from template")
        else:
            logger.info("Overwrote config.json with template")


if __name__ == "__main__":
    create_configJson(overwrite=True, take_input=True)
