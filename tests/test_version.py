import pytest
from genie.testbed import load
from ._inventory import devices_iosxe


@pytest.fixture(scope="session")
def tb():
    return load("testbed/testbed.yaml")


@pytest.mark.parametrize("d", devices_iosxe())
def test_hostname_matches_expected(tb, d):
    dev = tb.devices[d["name"]]
    dev.connect(log_stdout=False)
    try:
        line = dev.execute("show running-config | i ^hostname").strip()
        actual = line.split()[-1] if line else ""
        assert actual == d["expected_hostname"], f"{d['name']} hostname "
        f"'{actual}' != '{d['expected_hostname']}'"
    finally:
        if dev.is_connected():
            dev.disconnect()
