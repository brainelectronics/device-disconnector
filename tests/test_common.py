#!/usr/bin/env python3

import logging

from device_disconnector.common import LOG_LEVELS


def test_log_levels() -> None:
    assert LOG_LEVELS[0] == logging.CRITICAL
    assert LOG_LEVELS[1] == logging.ERROR
    assert LOG_LEVELS[2] == logging.WARNING
    assert LOG_LEVELS[3] == logging.INFO
    assert LOG_LEVELS[4] == logging.DEBUG
