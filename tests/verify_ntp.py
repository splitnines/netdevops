# import logging
from pyats import aetest
# from pyats.log.utils import banner


# log = logging.getLogger(__name__)
# log.info(banner("pyATS TDD Automated Network Testing"))


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_devices(self, testbed):
        testbed.connect(log_stdout=False)

    @aetest.subsection
    def loop_mark(self, testbed):
        aetest.loop.mark(TestNtpAssociationsReach, device_name=testbed.devices)


class TestNtpAssociationsReach(aetest.Testcase):
    @aetest.test
    def setup(self, testbed, device_name):
        self.device = testbed.devices[device_name]

    @aetest.test
    def show_ntp_associations(self):
        self.ntp_associations = self.device.parse("show ntp associations")
        if "peer" not in self.ntp_associations:
            self.failed(f"show_ntp_associations for {self.device.name} FAILED")

    @aetest.test
    def test_ntp_association_reach(self):
        self.ntp_reach_failed = False
        self.peer_ip_failed_list = []
        for peer_ip, peer_data in self.ntp_associations.get(
            "peer", {}
        ).items():
            for _, mode_data in peer_data.get("local_mode", {}).items():
                reach_value = mode_data.get("reach")
                if reach_value != 377:
                    self.ntp_reach_failed = True
                    self.peer_ip_failed_list.append(peer_ip)
        if self.ntp_reach_failed is True:
            self.failed_peers = ", ".join(self.peer_ip_failed_list)
            self.failed(
                "test_ntp_association_reach FAILED for "
                f"{self.device.name} on peers {self.failed_peers}"
            )

    @aetest.test
    def test_ntp_association_clock_state(self):
        ntp_clock_state = (
            self.ntp_associations["clock_state"]
            .get("system_status")
            .get("clock_state")
        )
        if ntp_clock_state is not None and ntp_clock_state != "synchronized":
            self.failed(
                "test_ntp_association_clock_state for "
                f"{self.device.name} FAILED"
            )


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        testbed.disconnect()


if __name__ == "__main__":
    aetest.main
