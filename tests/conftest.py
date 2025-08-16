# tests/conftest.py  — REPLACE ENTIRE FILE
import pytest
from genie.testbed import load

# Load the testbed once for the whole session
TESTBED = load("testbed/testbed.yaml")


@pytest.fixture(scope="session")
def tb():
    return TESTBED


def pytest_generate_tests(metafunc):
    """
    If a test function asks for 'dev_name', parametrize it with
    ALL device names from the loaded testbed.
    """
    if "dev_name" in metafunc.fixturenames:
        names = list(TESTBED.devices.keys())
        metafunc.parametrize("dev_name", names, ids=names)
