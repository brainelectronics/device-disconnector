#!/usr/bin/env python3

from argparse import ArgumentTypeError
from typing import List, Mapping, Tuple, Union

# import requests_mock
from unittest.mock import MagicMock, patch

import pytest

from device_disconnector.cli import (
    check_rest_api_support,
    control_ports,
    custom_type,
    parse_bool,
)


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

@patch('device_disconnector.cli.check_rest_api_support')
@pytest.mark.parametrize(
    "parsed_controls, ip, support_rest_api, expectation",
    [
        ({'switch': {'1': True}}, "http://192.168.178.50", False, [{"pinD4": "on"}]),
        ({'usb': {'0': True, '1': False}, 'switch': {'1': True}}, "http://192.168.178.50", False, [{"pinD0": "on"}, {"pinD1": "off"}, {"pinD4": "on"}]),
        ({'switch': {'1': True}}, "http://192.168.178.50", True, [{"switch1": "on"}]),
        ({'usb': {'0': True, '1': False}, 'switch': {'1': True}}, "http://192.168.178.50", True, [{"usb0": "on", "usb1": "off", "switch1": "on"}]),
    ]
)
def test_control_ports(mock_function, parsed_controls: Mapping[str, Mapping[str, bool]], ip: str, support_rest_api: bool, expectation: List[Mapping[str, str]]) -> None:
    mock_function.return_value = support_rest_api
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        mock_post.status_code = 200

        control_ports(parsed_controls=parsed_controls, ip=ip)

        if support_rest_api:
            assert mock_post.call_count == 1
            mock_post.assert_called_once_with(f"{ip}/set", data=expectation[0], timeout=10)

        else:
            assert (mock_post.call_count) == len(expectation)
            for idx, data in enumerate(expectation):
                mock_post.assert_any_call(
                    ip,
                    data=data,
                    timeout=10
                )

@pytest.mark.parametrize(
    "status_code, expectation",
    [
        (200, True),
        (404, False),
    ]
)
def test_check_rest_api_support(status_code: int, expectation: bool) -> None:
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = status_code
        ip = "http://192.168.178.50"
        endpoint = "/get/version"

        result = check_rest_api_support(ip=ip)
        assert result == expectation
        mock_get.assert_called_once_with(f"{ip}{endpoint}", timeout=10)
