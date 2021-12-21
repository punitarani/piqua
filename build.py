# Builds folders and files

from configurator.create_files_folders import createFiles
from configurator.create_files_folders import createFolders
from configurator.generate_configJson import create_configJson

from lib.tda.auth import Authenticate


if __name__ == "__main__":
    print("Options: ")
    print("(1) Complete\n"
          "(2) Create/Edit config.json\n"
          "(3) Authenticate TDA API\n")
    option = int(input("Enter build config option (1-3): "))

    if option == 1:
        createFolders()
        createFiles()

        create_configJson(overwrite=True, take_input=True)

    if option == 2:
        create_configJson(overwrite=True, take_input=True)

    if option == 3:
        Authenticate(generate_new_refresh_token=True)
