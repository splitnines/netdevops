import pytest
from genie.testbed import load
from ._inventory import devices_iosxe


@pytest.fixture(scope="session")
def tb():
    return load("testbed/testbed.yaml")


@pytest.mark.parametrize("d", devices_iosxe())
def test_mgmt_interface_up_up(tb, d):
    dev = tb.devices[d["name"]]
    dev.connect(log_stdout=False)
    try:
        parsed = dev.parse("show ip interface brief")
        ent = parsed["interface"].get(d["mgmt_int"])
        assert ent, f"{d['name']} missing {d['mgmt_int']}"
        assert ent["status"] == "up" and ent["protocol"] == "up", (
            f"{d['name']} "
        )
        f"{d['mgmt_int']} not up/up: {ent}"
    finally:
        if dev.is_connected():
            dev.disconnect()
