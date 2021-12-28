# Create necessary Files
# Run when setting up the project for the first time

import os
from pathlib import Path

from defs import ROOT
from src.loggers import SystemLogger

logger = SystemLogger("main").logger


# Folders to create
folders = [
    "data",
    "logs",
    "temp"
]


# Files to create
files = [
    "logs/system.log",
    "config.json",
    "logs/tda.log"
]


# Function to create folders
def createFolders():
    logger.info("Creating necessary folders")

    for folder in folders:
        folder_path = os.path.join(ROOT, folder)

        if os.path.exists(folder_path):
            logger.info("Folder already exists: {}".format(folder_path))

        else:
            os.makedirs(folder_path)
            logger.info("Folder created {}".format(folder_path))


# Function to create files
def createFiles():
    logger.info("Creating necessary files")

    for file in files:
        file_path = os.path.join(ROOT, file)

        # Create file if it doesn't exist
        if os.path.exists(file_path):
            logger.info("File already exists: {}".format(file_path))

        else:
            Path(file_path).touch(exist_ok=True)
            logger.info("File created: {}".format(file_path))


if __name__ == "__main__":
    createFolders()
    createFiles()
