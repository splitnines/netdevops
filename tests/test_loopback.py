import pytest
from genie.testbed import load


@pytest.fixture(scope="session")
def tb():
    return load("testbed/testbed.yaml")


def test_loopback0_description(tb):
    dev = tb.devices["r1"]
    dev.connect(log_stdout=False)
    try:
        out = dev.execute("show run interface Loopback0")
        assert "description configured via pipeline" in out, (
            "Loopback0 missing expected description"
        )
    finally:
        if dev.is_connected():
            dev.disconnect()
