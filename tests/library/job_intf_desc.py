import os
from genie.testbed import load


TESTBED = "all_devices.yaml"
TESTSUITE = "show_interface_desc.py"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def main(runtime):

    if runtime.testbed:
        testbed = runtime.testbed
    else:
        testbedfile = os.path.join(
            BASE_DIR, "tests", "config", "testbeds", TESTBED
        )
        testbed = load(testbedfile)

    testscript = os.path.join(BASE_DIR, "tests", "test_suites", TESTSUITE)
    runtime.tasks.run(testscript=testscript, testbed=testbed)
