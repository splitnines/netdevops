import pytest
from unicon.core.errors import ConnectionError


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
