# Chromedriver installing, upgrading and testing

import os
from urllib.request import urlopen
from zipfile import ZipFile

import requests
import selenium
import selenium.common.exceptions
from selenium import webdriver

from defs import CHROMEDRIVER, DRIVERS, TEMP, PLATFORM
from src.loggers import SystemLogger


class Chromedriver:
    def __init__(self, install_missing_files: bool = False):

        # OS platform specific variables
        if PLATFORM == "win32":
            self.os_suffix = "win32"
            self.CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

        elif PLATFORM == "linux":
            self.os_suffix = "linux64"
            self.CHROME_PATH = "/usr/bin/google-chrome"

        elif PLATFORM == "darwin":
            self.os_suffix = "mac64"
            self.CHROME_PATH = "/Applications/Google/Chrome.app"

        # Defaults to windows
        else:
            self.os_suffix = "win32"

        self.driver_zip_dir = os.path.join(TEMP)

        # Setup logger
        self.logger = SystemLogger("chromedriver").logger

        # Download chromedriver if missing
        if install_missing_files and not os.path.exists(CHROMEDRIVER):
            self.logger.error("chromedriver.exe missing.")
            self.download_chromedriver("MATCH")

    # Chrome and chromedriver Main Function
    def main(self):

        # Check if Chrome and chromedriver are installed
        if not self.check_installed():
            self.download_chromedriver()
            self.download_chrome()

        # Test to see if Chrome and chromedriver are working
        self.test()

    # Test if chrome browser works through selenium
    def test(self) -> None:
        self.logger.info("Testing Chromedriver.")

        try:
            browser = webdriver.Chrome(executable_path=CHROMEDRIVER)

            # Test if google works
            browser.get(url="https://www.google.com")
            browser.close()
            self.logger.info("Chrome and chromedriver are working correctly.")

        # WebDriverException:   Version mismatch
        # FileNotFoundError:   Missing chromedriver
        except selenium.common.exceptions.WebDriverException or FileNotFoundError:
            self.logger.error("Chromedriver is not working correctly.")

            if not os.path.exists(CHROMEDRIVER):
                self.logger.info("Attempting to download chromedriver.exe.")
            else:
                self.logger.info("Attempting to upgrade chromedriver.exe.")

            self.download_chromedriver()

            browser = webdriver.Chrome(executable_path=CHROMEDRIVER)

            # Test if google works
            browser.get(url="https://www.google.com")
            browser.close()
            self.logger.info("Chrome and chromedriver are working correctly.")

    # Check if files are installed
    def check_installed(self, raise_error: bool = False) -> bool:
        missing_files = []
        self.logger.debug("Checking for Chrome and chromedriver files.")

        # Checks if chromedriver is installed
        if not os.path.exists(CHROMEDRIVER):
            self.logger.error("chromedriver.exe missing.")
            missing_files.append("chromedriver.exe")

        # Checks if chrome browser is installed
        if not os.path.exists(self.CHROME_PATH):
            self.logger.error("Chrome browser missing.")
            missing_files.append("Chrome")

        if len(missing_files) > 0:
            if raise_error:
                msg = "Missing files: " + ", ".join(missing_files)
                self.logger.error(msg)
                raise FileNotFoundError(msg)
            else:
                return False
        else:
            self.logger.info("All files are installed.")
            return True

    # Returns installed chrome browser version
    # chromedriver: gets the latest applicable chromedriver version to match the installed chrome browser
    def getChromeVersion(self, chromedriver: bool = True) -> str:
        try:
            driver = webdriver.Chrome(CHROMEDRIVER)

            if 'browserVersion' in driver.capabilities:
                version = driver.capabilities['browserVersion']
            else:
                version = driver.capabilities['version']

        # WebDriverException:   Version mismatch
        # FileNotFoundError:    Missing chromedriver
        except selenium.common.exceptions.WebDriverException or FileNotFoundError:
            files = os.listdir(os.path.normpath(self.CHROME_PATH + os.sep + os.pardir))

            """
            Example:
            files = ['96.0.4664.110', 'chrome.exe', 'chrome.VisualElementsManifest.xml',
            'chrome_proxy.exe', 'master_preferences', 'SetupMetrics']
            """

            files.sort()
            version = files[0]

        # Gets latest chromedriver for installed chrome browser version
        if chromedriver:
            version = requests.get(f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version[0:2]}") \
                .content.decode()

        return version

    # Get latest available stable chromedriver version
    @staticmethod
    def latest_version() -> str:
        version = requests.get(url="https://chromedriver.storage.googleapis.com/LATEST_RELEASE").content.decode()
        return version

    # Download chromedriver version
    def download_chromedriver(self, version: str = "LATEST") -> None:
        # Latest Version
        if (version is None) or (version.upper() == "LATEST"):
            version = self.latest_version()
            self.logger.debug(f"Latest Version: {version}")

        # Match installed Chrome browser version
        if (version is None) or (version.upper() == "MATCH"):
            version = self.getChromeVersion(chromedriver=True)
            self.logger.debug(f"Match Version: {version}")

        # Download chromedriver zip
        url = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_{self.os_suffix}.zip"

        self.logger.info(f"Downloading: {url}")
        driver_zip_url = urlopen(url)
        driver_zip_path = os.path.join(self.driver_zip_dir, f"chromedriver_{version}.zip")
        with open(driver_zip_path, "wb") as driver:
            driver.write(driver_zip_url.read())

        # Rename if chromedriver already exists
        if os.path.exists(CHROMEDRIVER):
            self.logger.debug("Renaming existing chromedriver.exe to chromedriver_old.exe.")
            os.rename(CHROMEDRIVER, (CHROMEDRIVER.split(".exe")[0] + "_old.exe"))

        # Unzip driver
        self.logger.debug("Unzipping chromedriver.exe.")
        driver_zip = ZipFile(driver_zip_path)
        driver_zip.extractall(path=DRIVERS)

    # Download chrome browser
    def download_chrome(self) -> bool:
        # Check if chrome browser is installed
        if os.path.exists(self.CHROME_PATH):
            self.logger.info("Chrome browser already installed.")
            return True

        # For windows or MacOs
        if PLATFORM == "win32" or PLATFORM == "darwin":
            url = "https://www.google.com/chrome/"
            self.logger.info(f"Download from: {url}")

        # For linux
        elif PLATFORM == "linux":
            cli_mode = input("CLI or GUI mode? (CLI/GUI): ")
            if cli_mode.upper() == "CLI":
                self.logger.info("To install Chrome, run the following commands:")
                self.logger.info("sudo apt-get install wget")
                self.logger.info("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
                self.logger.info("sudo dpkg -i google-chrome-stable_current_amd64.deb")

            elif cli_mode.upper() == "GUI":
                url = "https://www.google.com/chrome/"
                self.logger.info(f"Download from: {url}")

            install = input("Do you want to install Google Chrome? (y/n) ").lower()
            if install == "y":
                try:
                    self.logger.info("Installing Google Chrome.")

                    self.logger.info("Installing wget.")
                    os.system("sudo apt-get install wget")

                    self.logger.info("Downloading Google Chrome.")
                    os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")

                    self.logger.info("Installing Google Chrome.")
                    os.system("sudo dpkg -i google-chrome-stable_current_amd64.deb")

                    self.logger.info("Removing Google Chrome deb file.")
                    os.system("rm google-chrome-stable_current_amd64.deb")

                    self.logger.info("Google Chrome installed.")
                    return True

                except Exception as e:
                    self.logger.error(f"Error: {e}")
                    self.logger.error("Google Chrome not installed.")
                    self.logger.error("Please install Google Chrome manually.")

        # Continue when done
        self.logger.info("\nContinue after installing Google Chrome manually.")
        install = input("Did you install Google Chrome? (y/n) ").lower()
        if install == "y":
            return True
        else:
            return False


if __name__ == "__main__":
    Chromedriver(install_missing_files=True).main()
