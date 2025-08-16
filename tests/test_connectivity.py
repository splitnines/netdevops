import pytest
from genie.testbed import load
from unicon.core.errors import ConnectionError


@pytest.fixture(scope="session")
def tb():
    return load("testbed/testbed.yaml")


@pytest.mark.parametrize("dev_name", ["r1", "sw2-1"])
def test_connect_cli(tb, dev_name):
    dev = tb.devices[dev_name]
    try:
        dev.connect(log_stdout=False)
        dev.execute("show clock")
    except ConnectionError as e:
        pytest.fail(f"Failed to connect to {dev_name}: {e}")
    finally:
        if dev.is_connected():
            dev.disconnect()
