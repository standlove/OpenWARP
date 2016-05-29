# -*- coding: utf-8 -*-
"""
This module starts the cli. 
"""

__author__ = "TCSASSEMBLER"
__copyright__ = "Copyright (C) 2016 TopCoder Inc. All rights reserved."
__version__ = "1.0"

from openwarp.cli import OpenWarpCLI
from openwarp.settings import *

from nemoh import utility
from nemoh import settings

if __name__ == '__main__':
    # setup logging
    utility.setup_logging(default_conf_path=settings.LOGGING_CONFIGURATION_FILE, logging_path=LOG_FILE)

    # start the cli
    OpenWarpCLI().cmdloop()