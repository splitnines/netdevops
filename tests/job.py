from pyats.easypy import run


def main(runtime):
    runtime.job.name = "verify_ntp.py"

    run(
        testscript="tests/verify_ntp.py",
        testbed="testbed.yaml",
        runtime=runtime,
    )
