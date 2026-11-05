"""Unit tests for CDB firmware version prerequisites."""

import pytest

from tests.transceiver.attribute_parser.attribute_keys import CDB_FIRMWARE_UPGRADE_ATTRIBUTES_KEY
from tests.transceiver.cdb_firmware_upgrade.utils.firmware_utils import (
    select_distinct_version,
    validate_distinct_firmware_versions,
)


def _port(versions, gold="1.0.0"):
    return {
        CDB_FIRMWARE_UPGRADE_ATTRIBUTES_KEY: {
            "firmware_versions": versions,
            "gold_firmware_version": gold,
        },
    }


@pytest.mark.parametrize(
    "versions,gold,expected",
    [
        (["1.1.0", "255.0.0", "1.0.0"], "1.0.0", None),
        (["1.1.1", "255.0.0", "1.0.0"], "1.0.0", "1.1.1"),
        (["1.1.0", "1.0.1", "1.0.0"], "1.0.0", None),
        (["1.1", "1.0"], "1.0", None),
        (["1.1.1.0", "1.0.0.0"], "1.0.0.0", "1.1.1.0"),
        (["1.1.0.1", "1.0.0.0"], "1.0.0.0", None),
    ],
)
def test_select_distinct_version(versions, gold, expected):
    assert select_distinct_version(versions, gold) == expected


def test_invalid_port_skips_the_suite_with_port_reason():
    attributes = {
        "Ethernet0": _port(["1.1.1", "1.0.2", "1.0.0"]),
        "Ethernet96": _port(["1.1.0", "255.0.0", "1.0.0"]),
        "Ethernet100": _port(["1.1.0", "255.0.0", "1.0.0"]),
    }

    with pytest.raises(pytest.skip.Exception) as exc:
        validate_distinct_firmware_versions(attributes, ["Ethernet0", "Ethernet96", "Ethernet100"])

    message = str(exc.value)
    assert "Ethernet96: no firmware version differs from gold in both minor and point" in message
    assert "Ethernet100: no firmware version differs from gold in both minor and point" in message
    assert "Ethernet0:" not in message


def test_valid_ports_pass_and_unselected_ports_are_ignored():
    attributes = {
        "Ethernet0": _port(["1.1.1", "1.0.2", "1.0.0"]),
        "Ethernet96": _port(["1.1.0", "255.0.0", "1.0.0"]),
    }

    validate_distinct_firmware_versions(attributes, ["Ethernet0"])


@pytest.mark.parametrize(
    "attrs",
    [
        {},
        {"firmware_versions": []},
        {"firmware_versions": ["1.0.0"], "gold_firmware_version": None},
    ],
)
def test_incomplete_attributes_remain_for_metadata_validation(attrs):
    attributes = {"Ethernet0": {CDB_FIRMWARE_UPGRADE_ATTRIBUTES_KEY: attrs}}
    validate_distinct_firmware_versions(attributes, ["Ethernet0"])
