import os
from genie.testbed import load


def main(runtime):
    if not runtime.testbed:
        testbedfile = os.path.join("tests", "testbed.yaml")
        testbed = load(testbedfile)
    else:
        testbed = runtime.testbed

    testscript = os.path.join(os.path.dirname(__file__), "verify_ntp.py")

    runtime.tasks.run(testscript=testscript, testbed=testbed)
