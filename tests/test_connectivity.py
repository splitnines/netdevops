# import pytest
# from unicon.core.errors import ConnectionError
#
#
# def test_connect_cli(tb, dev_name):
#     dev = tb.devices[dev_name]
#     try:
#         dev.connect(log_stdout=False)
#         dev.execute("show clock")
#     except ConnectionError as e:
#         pytest.fail(f"Failed to connect to {dev_name}: {e}")
#     finally:
#         if dev.is_connected():
#             dev.disconnect()
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
        dev.connect(log_stdout=False)
        dev.execute("show clock")
    except ConnectionError as e:
        pytest.fail(f"Failed to connect to {dev}: {e}")
    finally:
        if dev.is_connected():
            dev.disconnect()
