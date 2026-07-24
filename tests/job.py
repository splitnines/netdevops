import os
from genie.testbed import load


TESTBED = "cml_consoles.yaml"
TESTSUITE = "ospfv2_test_suite.py"

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
