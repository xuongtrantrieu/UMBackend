# -*- coding: utf-8 -*-
########################################################################
#
#    Logger <<Singleton>>
#
########################################################################
import os, sys
path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
if path not in sys.path:
    sys.path.append(path)

import logging
import logging.handlers
import time
from configparser import ConfigParser

from django.conf import settings

PATH_CONFIG = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "conf", "config.ini"))

class Logger(object):
    def __init__(self, path=PATH_CONFIG):
        # default settings

        self._config = ConfigParser()
        self._config.read(path)

        self.setEnable(self._config.getboolean("Logging", "Enable"))
        self.setLogLevel(self._config.get("Logging", "LogLevel"))
        self.setLogDir(self._config.get("Logging", "LogDir"))
        self.setLogname(self._config.get("Logging", "LogFilename"))
        self.setMaxLogSize(self._config.getint("Logging", "MaxLogSize"))
        self.setBackupCount(self._config.getint("Logging", "BackupCount"))

        self._logger = None
        return

    def _makeLogger(self):
        # return, if logger is already exists.
        if self._logger is not None:
            return

        # log path
        path = os.path.abspath(os.path.join(self._logDir, self._logname))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        # set logging
        self._logger = logging.getLogger('')
        self._logger.setLevel(self._logLevel)
        handler = logging.handlers.RotatingFileHandler(path, maxBytes=self._maxLogSize, backupCount=self._backupCount)
        self._logger.addHandler(handler)
        #formatter = "%(asctime)s(UTC): %(levelname)s: %(module)s.%(funcName)s: %(message)s"   # AA '%(hostname)s':
        formatter = "%(asctime)s(UTC): %(levelname)s: %(message)s"
        logging.Formatter.converter = time.gmtime
        handler.setFormatter(logging.Formatter(formatter))
        return

    # Enable
    def setEnable(self, flag=True):
        if isinstance(flag, bool):
            self._enable = flag
        else:
            raise TypeError
        return

    def isEnable(self):
        return self._enable

    # LogLevel
    def setLogLevel(self, logLevel):
        self._logLevel = getattr(logging, logLevel, getattr(logging, "INFO"))
        return

    # LogDir
    def setLogDir(self, logDir):
        self._logDir = os.path.join(settings.BASE_DIR, logDir)
        return

    # Logname
    def setLogname(self, logname):
        if not hasattr(self, "_logname"):
            self._logname = logname
        return

    # maxLogSize
    def setMaxLogSize(self, maxLogSize):
        self._maxLogSize = maxLogSize
        return

    # backupCount
    def setBackupCount(self, backupCount):
        self._backupCount = backupCount
        return

    # Logging
    def debug(self, msg, *args, **kwargs):
        if self._enable:
            self._makeLogger()
            self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self._enable:
            self._makeLogger()
            self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self._enable:
            self._makeLogger()
            self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self._enable:
            self._makeLogger()
            self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self._enable:
            self._makeLogger()
            self._logger.critical(msg, *args, **kwargs)

if __name__ == '__main__':
    # test 1: default logger
    """
    Logger().debug("Debug")
    Logger().info("Info")
    Logger().warning("Warning")
    Logger().error("Error")
    Logger().critical("Critical")
    """

    # test 2: another logger
    # Logger().setLogDir("/tmp")
    # Logger().setLogname("test.log")
    # Logger().setLogLevel("INFO")
    # Logger().debug("Debug")
    # Logger().info("Info")
    # Logger().warning("Warning")
    # Logger().error("Error")
    # Logger().critical("Critical")
    print (PATH_CONFIG)
    Logger().info("code_velifier        : {0}".format("dffff"))
