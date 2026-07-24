from pyats import aetest

from test_suites.test_scripts.eigrp.ipv6_interfaces_test import (
    TestEigrpV6Interfaces,
)


class Setup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_devices(self, testbed):
        testbed.connect(log_stdout=False)

    @aetest.subsection
    def loop_mark(self, testbed):
        for testcase in testcases:
            aetest.loop.mark(
                testcase,
                device_name=list(testbed.devices),
            )


class TestEigrpV6Interfaces(TestEigrpV6Interfaces):
    pass


testcases = [
    TestEigrpV6Interfaces,
]


class Cleanup(aetest.CommonCleanup):
    @aetest.subsection
    def restore_console(self, testbed, steps):
        for device in testbed.devices.values():
            with steps.start(
                f"Reset terminal settings on {device.name}", continue_=True
            ) as step:
                if not device.is_connected():
                    step.skipped(f"{device.name} not connected")
                    continue

                try:
                    device.execute(
                        [
                            "terminal length 24",
                            "terminal width 80",
                        ]
                    )
                except Exception as exc:
                    step.passx(f"Could not reset terminal settings: {exc}")

            with steps.start(
                f"Restore console logging on {device.name}", continue_=True
            ) as step:
                if not device.is_connected():
                    step.skipped(f"{device.name} not connected")
                    continue
                try:
                    device.configure("logging console")
                except Exception as exc:
                    step.passx(f"Cound not restore console loggin {exc}")

    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        testbed.disconnect()


if __name__ == "__main__":
    aetest.main()
