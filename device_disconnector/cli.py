#!/usr/bin/env python3

"""Disconnect devices with REST calls to IP based Device Disconnector"""

import logging
from argparse import ArgumentParser, ArgumentTypeError
from argparse import Namespace as Args
from re import findall
from sys import stdout
from time import sleep
from typing import Mapping, Sequence, Tuple, Union

import requests

from .common import LOG_LEVELS

LOGGER_FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(filename)-15s @'\
                ' %(funcName)-15s:%(lineno)4s] %(message)s'

# configure logging
logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT, stream=stdout)

logger = logging.getLogger("device_disconnector")
logger.setLevel(logging.DEBUG)


def parse_bool(value: Union[str, int, bool]) -> bool:
    """Convert string to boolean"""
    if value == 1:
        return True
    elif isinstance(value, str) and value.lower() in ("on", "true", "1", "active"):
        return True
    return False


def custom_type(arg_string: str) -> Tuple[str, bool]:
    """Custom argument type for key-value pairs"""
    suggestion = "use 'usb0=on' or 'switch1=off'"
    parts = arg_string.split('=')
    if len(parts) != 2 or parts[1] == "":
        raise ArgumentTypeError(f"Invalid format: {arg_string}, {suggestion}")

    key, value = parts
    try:
        bool_value = parse_bool(value)
    except ValueError:
        raise ArgumentTypeError(f"Invalid value for {key}: {value}, {suggestion}")

    if len(findall(r'[A-Za-z]+|\d+', key)) != 2:
        raise ArgumentTypeError(f"Invalid format: {arg_string}, use {suggestion}")

    return key, bool_value


def parse_args(argv: Union[Sequence[str], None] = None) -> Args:
    """Multi command argument parser"""
    parser = ArgumentParser(__doc__)
    parser.add_argument(
        "--verbose", "-v",
        default=0,
        action="count",
        help="Set level of verbosity, default is CRITICAL",
    )

    parser.add_argument(
        "ip",
        help="IP address of Device Disconnector",
    )

    parser.add_argument(
        "ports",
        nargs='+',
        help="USB port states (e.g., usb0=on usb1=off)",
        type=custom_type
    )

    return parser.parse_args(argv)


def check_rest_api_support(ip: str) -> bool:
    response = requests.get(f"{ip}/get/version", timeout=10)
    if response.status_code == requests.codes.ok:
        logger.debug(f"Device software version: {response.json()}")
        return True

    return False


def control_ports(parsed_controls: Mapping[str, Mapping[str, bool]], ip: str) -> None:
    if any(key not in ("usb", "switch") for key in parsed_controls.keys()):
        raise NotImplementedError("Only 'usb' and 'switch' supported")

    if check_rest_api_support(ip=ip):
        control_ports_v4(parsed_controls=parsed_controls, ip=ip)
    else:
        control_ports_v3(parsed_controls=parsed_controls, ip=ip)


def control_ports_v4(parsed_controls: Mapping[str, Mapping[str, bool]], ip: str) -> None:
    data = {}
    for ports, elements in parsed_controls.items():
        logger.debug(f"ports: {ports}, elements: {elements}")
        for port, state in elements.items():
            data[f"{ports}{port}"] = "on" if state else "off"

    logger.debug(data)
    response = requests.post(f"{ip}/set", data=data, timeout=10)
    if response.status_code != requests.codes.ok:
        logger.warning(f"Failed to post '{data}' to '{ip}'")


def control_ports_v3(parsed_controls: Mapping[str, Mapping[str, bool]], ip: str) -> None:
    for ports, elements in parsed_controls.items():
        pin = "pinD"
        data = {}
        if ports == "usb":
            pin_offset = 0
        elif ports == "switch":
            pin_offset = 3

        logger.debug(f"ports: {ports}, elements: {elements}")
        # ports: usb, elements: {'1': False}

        for port, state in elements.items():
            data = {f"{pin}{int(port) + pin_offset}": "on" if state else "off"}
            logger.debug(data)
            response = requests.post(ip, data=data, timeout=10)
            if response.status_code != requests.codes.ok:
                logger.warning(f"Failed to post '{data}' to '{ip}'")
            sleep(0.5)


def main() -> int:
    """Entry point for everything else"""
    args = parse_args()

    log_level = LOG_LEVELS[min(args.verbose, max(LOG_LEVELS.keys()))]
    logger.setLevel(level=log_level)
    logger.debug(f"{args}, {log_level}")

    ip = f"{'http://' if not args.ip.startswith('http://') else ''}{args.ip}"

    # Parse the input string into a dictionary
    parsed_controls = {"usb": {}, "switch": {}}
    for key, value in args.ports:
        # ('usb0', True)
        control_type, control_id = findall(r'[A-Za-z]+|\d+', key)
        parsed_controls[control_type][control_id] = value

    logger.debug(f"Ports: {parsed_controls}")

    control_ports(parsed_controls=parsed_controls, ip=ip)

    return 0


if __name__ == "__main__":
    main()
