# Builds folders and files

from configurator.create_files_folders import createFiles
from configurator.create_files_folders import createFolders
from configurator.generate_configJson import create_configJson


if __name__ == "__main__":
    createFolders()
    createFiles()

    create_configJson(overwrite=True, take_input=True)
