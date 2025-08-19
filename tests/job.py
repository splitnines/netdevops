# def main(runtime):
#     runtime.job.name = "verify_ntp.py"
#
#     runtime.tasks.run(
#         testscript="tests/verify_ntp.py",
#         testbed="tests/testbed.yaml",
#         runtime=runtime,
#     )
#
#
import os
from genie.testbed import load


def main(runtime):
    # ----------------
    # Load the testbed
    # ----------------
    if not runtime.testbed:
        # If no testbed is provided, load the default one.
        # Load default location of Testbed
        testbedfile = os.path.join("tests", "testbed.yaml")
        testbed = load(testbedfile)
    else:
        # Use the one provided
        testbed = runtime.testbed

    # Find the location of the script in relation to the job file
    testscript = os.path.join(os.path.dirname(__file__), "verify_ntp.py")

    # run script
    runtime.tasks.run(testscript=testscript, testbed=testbed)
