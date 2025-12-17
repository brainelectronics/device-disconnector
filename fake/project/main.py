#!/usr/bin/env python3
import logging
from enum import Enum
from random import randint

from flask import Flask, jsonify, make_response, render_template, request

app = Flask(__name__)

NUMBER_USB_PORTS = 4
NUMBER_SWITCH_PINS = 4
SWITCH_PINS_OFFSET = 4

usb_locks = [0] * NUMBER_USB_PORTS
switch_locks = [0] * NUMBER_SWITCH_PINS
sr = dict(enumerate(randint(0, 1) for _ in range(0, NUMBER_USB_PORTS + NUMBER_SWITCH_PINS)))
isoTimeBuffer = "2025-01-11T22-19-10"

class Port(Enum):
  UNKNOWN = 0
  USB_PIN = 1
  SWITCH_PIN = 2
  LOCK = 3


logging.basicConfig(
    format="[%(asctime)s] [%(levelname)-8s] [%(funcName)-15s:%(lineno)4s] %(message)s",
    level=logging.DEBUG,
)
# LOG = logging.getLogger(__name__)
LOG = logging.getLogger("werkzeug")

@app.route("/")
def hello_world():
    # return "<p>Hello, World!</p>"
    return render_template(
        "index.html",
        NUMBER_USB_PORTS=NUMBER_USB_PORTS,
        NUMBER_SWITCH_PINS=NUMBER_SWITCH_PINS,
        SWITCH_PINS_OFFSET=SWITCH_PINS_OFFSET,
        usb_locks=usb_locks,
        switch_locks=switch_locks,
        sr=sr,
        isoTimeBuffer=isoTimeBuffer,
    )

@app.route('/get', methods=['GET'])
def get_keys():
    return jsonify({"keys": ["usb", "switch", "lock", "version"]})

@app.route('/get/all', methods=['GET'])
def get_all():
    return jsonify({"usb":  pin_state_json(first=0, last=NUMBER_USB_PORTS, offset=0), "switch": pin_state_json(first=SWITCH_PINS_OFFSET, last=SWITCH_PINS_OFFSET + NUMBER_SWITCH_PINS, offset=SWITCH_PINS_OFFSET), "lock": dict(enumerate(usb_locks + switch_locks))})

@app.route('/get/lock', methods=['GET'])
def get_lock():
    return jsonify({"lock": dict(enumerate(usb_locks + switch_locks))})

@app.route('/get/switch', methods=['GET'])
def get_switch() -> dict:
    return jsonify({"switch": pin_state_json(first=SWITCH_PINS_OFFSET, last=SWITCH_PINS_OFFSET + NUMBER_SWITCH_PINS, offset=SWITCH_PINS_OFFSET)})

@app.route('/get/usb', methods=['GET'])
def get_usb() -> dict:
    return jsonify({"usb": pin_state_json(first=0, last=NUMBER_USB_PORTS, offset=0)})

@app.route('/get/version', methods=['GET'])
def get_version():
    LOG.info("get_version bla bla")
    return jsonify({"version": "1.2.3", "sha": "asdf", "created": isoTimeBuffer})

@app.route('/set', methods=['POST'])
def set_value() -> None:
    post_data = dict(request.form)
    return_code = 200
    range_end = 0

    for key, val in post_data.items():
        LOG.info(f"Processing {key}: {val}")
        state = 0
        pin_or_port_number = int(key[-1])

        if val in ("on", "ON", 1, True):
            state = 1

        match pin_or_port(input_value=key):
            case Port.USB_PIN:
                LOG.info(f"State of USB pin {key}: {state}, number {pin_or_port_number}")
                if pin_or_port_number > (NUMBER_USB_PORTS - 1):
                    return_code = 416
                    range_end = NUMBER_USB_PORTS - 1
                    LOG.warning(f"Out of range, max {range_end}")
                if usb_locks[pin_or_port_number] == 0:
                    sr[pin_or_port_number] = state
                else:
                    LOG.warning("State not changed, currently locked")
                    return_code = 423
            case Port.SWITCH_PIN:
                LOG.info(f"State of Switch pin {key}: {state}, number + SWITCH_PINS_OFFSET {pin_or_port_number + SWITCH_PINS_OFFSET}")
                if pin_or_port_number > (NUMBER_SWITCH_PINS - 1):
                    return_code = 416
                    range_end = NUMBER_SWITCH_PINS - 1
                    LOG.warning(f"Out of range, max {range_end}")
                if switch_locks[pin_or_port_number - SWITCH_PINS_OFFSET] == 0:
                    sr[pin_or_port_number + SWITCH_PINS_OFFSET] = state
                else:
                    LOG.warning("State not changed, currently locked")
                    return_code = 423
            case Port.LOCK:
                LOG.info(f"State of USB pin {key}: {state}, number {pin_or_port_number}")
                if pin_or_port_number > (NUMBER_USB_PORTS + NUMBER_SWITCH_PINS - 1):
                    return_code = 416
                    range_end = NUMBER_USB_PORTS + NUMBER_SWITCH_PINS - 1
                    LOG.warning(f"Out of range, max {range_end}")
                if pin_or_port_number >= SWITCH_PINS_OFFSET:
                    LOG.info(f"This should be switch_locks {pin_or_port_number - SWITCH_PINS_OFFSET}")
                    switch_locks[pin_or_port_number - SWITCH_PINS_OFFSET] = state
                else:
                    LOG.info(f"This should be usb_locks {pin_or_port_number}")
                    usb_locks[pin_or_port_number] = state
            case _:
                LOG.info(f"Unknown input {key}")
                return_code = 422

        if return_code != 200:
            break

    match return_code:
        case 200:
            return jsonify({'success': True}), 200, {'ContentType': 'application/json'}
        case 416:
            return make_response(f"Content-Range: bytes 0-{range_end}/1", 416)
        case 422:
            data = {
                "message": "Unprocessable pin or port content. Applied as much config as possible, might still be incomplete.",
                "content": {key: val}
            }
            return jsonify(data), 422, {'ContentType': 'application/json'}
        case 423:
            data = {
                "message": "Resource locked",
                "content": {key: val}
            }
            return jsonify(data), 423, {'ContentType': 'application/json'}
        case _:
            data = {
                "message": "Unprocessable pin or port content. Applied as much config as possible, might still be incomplete.",
                "content": {key: val}
            }
            return jsonify(data), 422, {'ContentType': 'application/json'}


def lock_state_json() -> dict:
    return dict(enumerate(usb_locks + switch_locks))

def pin_state_json(first: int, last: int, offset: int=0) -> dict:
    # rework to yield from
    d = dict()
    for i in range(first, last):
        d[i - offset] = sr.get(i)
    return d

def pin_or_port(input_value: str) -> int:
    match input_value[:-1]:
        case "usb":
            return Port.USB_PIN
        case "switch":
            return Port.SWITCH_PIN
        case "lock":
            return Port.LOCK
        case _:
            return Port.UNKNOWN
