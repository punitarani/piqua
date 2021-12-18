# Definitions File

import os
import sys

# OS
PLATFORM = sys.platform

# Directories
ROOT = os.path.dirname(os.path.abspath(__file__))
TEMP = os.path.join(ROOT, "temp")
LOGS = os.path.join(ROOT, "logs")
DRIVERS = os.path.join(ROOT, "drivers")

# Log Files
SYSTEM_LOG = os.path.join(LOGS, "system.log")
TDA_LOG = os.path.join(LOGS, "tda.log")

# Config Files
CONFIG_JSON = os.path.join(ROOT, "config.json")

# Drivers
CHROMEDRIVER = os.path.join(DRIVERS, "chromedriver.exe")
