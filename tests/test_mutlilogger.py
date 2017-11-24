import logging
from unittest.mock import patch
from multilogger.logger import MultiLogger


def test_multilogger_log():
    logger = MultiLogger("test")
    logger.log()