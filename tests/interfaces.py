import os
import pytest
from genie.testbed import load


@pytest.fixture(scope="session")
def tb():
    return load("testbed/testbed.yaml")


CASES = [
    ("r1", "R1_MGMT_INT"),
    ("sw2-1", "SW2_1_MGMT_INT"),
]


@pytest.mark.parametrize("dev_name,env_key", CASES)
def test_mgmt_interface_up_up(tb, dev_name, env_key):
    mgmt_intf = os.environ.get(env_key)
    if not mgmt_intf:
        pytest.skip(f"{env_key} not set")
    dev = tb.devices[dev_name]
    dev.connect(log_stdout=False)
    try:
        parsed = dev.parse("show ip interface brief")
        # Genie normalized schema
        # parsed["interface"][<name>]["status"] == "up" and ["proto"] == "up"
        d = parsed["interface"].get(mgmt_intf)
        assert d, f"{dev_name} missing {mgmt_intf}"
        assert d["status"] == "up" and d["proto"] == "up", (
            f"{dev_name} {mgmt_intf} not up/up: {d}"
        )
    finally:
        if dev.is_connected():
            dev.disconnect()
