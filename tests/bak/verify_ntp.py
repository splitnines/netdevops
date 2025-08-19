from pyats import aetest
from genie.testbed import load


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect(self, testbed):
        testbed.connect()


class VerifyNTP(aetest.Testcase):
    @aetest.test
    def check_ntp(self, testbed):
        dev = testbed.devices["r1"]
        output = dev.parse("show ntp associations")
        assert output, "No NTP associations found"


class CommonCleanup(aetest.CommonCleanup):
    pass
