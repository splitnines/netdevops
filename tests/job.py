from pyats.easypy import run


def main(runtime):
    run(testscript="tests/verify_ntp.py", testbed="testbed.yaml")
