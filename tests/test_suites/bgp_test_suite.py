from pyats import aetest

from test_suites.test_scripts.bgp.bgp_neighbors_status import (
    TestBgpDefaultNeighborStatus,
)
from test_suites.test_scripts.eigrp.ipv4_interfaces_test import (
    TestEigrpInterfaces,
)


class Setup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_devices(self, testbed):
        testbed.connect(log_stdout=False)

    @aetest.subsection
    def loop_mark(self, testbed, device_groups):
        missing = [
            router
            for router in device_groups.get("eigrp")
            if router not in list(testbed.devices)
        ]

        if missing:
            self.fail(f"EIGRP routers missing from testbed {missing}")

        for eigrp_testcase in eigrp_testcases:
            aetest.loop.mark(
                eigrp_testcase,
                device_name=device_groups.get("eigrp"),
            )

        for testcase in testcases:
            aetest.loop.mark(
                testcase,
                device_name=list(testbed.devices),
            )


# subclass all test cases that need to be run
class TestBgpDefaultNeighborStatus(TestBgpDefaultNeighborStatus):
    pass


class TestEigrpInterface(TestEigrpInterfaces):
    pass


# Test cases that need to be looped
testcases = [
    TestBgpDefaultNeighborStatus,
]

eigrp_testcases = [
    TestEigrpInterfaces,
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
