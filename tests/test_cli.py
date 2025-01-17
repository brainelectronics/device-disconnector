#!/usr/bin/env python3

from argparse import ArgumentTypeError
from typing import List, Mapping, Tuple, Union

# import requests_mock
from unittest.mock import MagicMock, patch

import pytest

from device_disconnector.cli import control_ports, custom_type, parse_bool


@pytest.mark.parametrize(
    "value, expectation",
    [
        (1, True),
        (0, False),
        ("on", True),
        ("1", True),
        ("active", True),
        ("true", True),
        ("off", False),
        ("0", False),
        ("something", False),
    ]
)
def test_parse_bool(value: Union[str, int, bool], expectation: bool) -> None:
    assert parse_bool(value=value) == expectation


@pytest.mark.parametrize(
    "arg_string, expectation",
    [
        ("switch1=off", ("switch1", False)),
        ("usb0=on", ("usb0", True)),
        ("hans1=off", ("hans1", False)),

        # invalid format of key=value
        ("usb1", None),
        ("usb0=", None),

        # invalud value, can never happen as everything unknown results to False

        # invalid key
        ("usb=off", None),
        ("1=off", None),
    ]
)
def test_custom_type(arg_string: str, expectation: Union[Tuple[str, bool], None]) -> None:
    if expectation is None:
        with pytest.raises(ArgumentTypeError) as e_info:
            custom_type(arg_string=arg_string)

        assert f"Invalid format: {arg_string}" in str(e_info.value)
    else:
        assert custom_type(arg_string=arg_string) == expectation

@pytest.mark.parametrize(
    "parsed_controls, ip",
    [
        ({'usb2': {'0': True, '1': False}, 'switch': {'1': True}}, "http://192.168.178.50"),
        ({'usb': {'0': True, '1': False}, 'switch2': {'1': True}}, "http://192.168.178.50"),
        ({'usb2': {'0': True, '1': False}, 'switch2': {'1': True}}, "http://192.168.178.50"),
    ]
)
def test_control_ports_raise(parsed_controls: Mapping[str, Mapping[str, bool]], ip: str) -> None:
    with pytest.raises(NotImplementedError) as e_info:
        control_ports(parsed_controls=parsed_controls, ip=ip)
    assert "Only 'usb' and 'switch' supported" in str(e_info.value)

@pytest.mark.parametrize(
    "parsed_controls, ip, expectation",
    [
        ({'switch': {'1': True}}, "http://192.168.178.50", [{"pinD4": "on"}]),
        ({'usb': {'0': True, '1': False}, 'switch': {'1': True}}, "http://192.168.178.50", [{"pinD0": "on"}, {"pinD1": "off"}, {"pinD4": "on"}]),
    ]
)
def test_control_ports(parsed_controls: Mapping[str, Mapping[str, bool]], ip: str, expectation: List[Mapping[str, str]]) -> None:
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        mock_post.status_code = 200

        control_ports(parsed_controls=parsed_controls, ip=ip)

        assert (mock_post.call_count) == len(expectation)
        for idx, data in enumerate(expectation):
            mock_post.assert_any_call(
                ip,
                data=data,
                timeout=10
            )