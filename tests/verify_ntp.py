import logging

# from genie.testbed import load
# from rich.console import Console
# from rich.table import Table
from pyats import aetest
from pyats.log.utils import banner


log = logging.getLogger(__name__)
log.info(banner("pyATS TDD Automated Network Testing"))

# console = Console()


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all the devices"""
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
        # table = Table(
        #     title="Show NTP Associations Test", title_style="bold magenta"
        # )
        # table.add_column("Device", justify="center", style="cyan")
        # table.add_column("Test Status", justify="center", style="cyan")
        self.ntp_associations = self.device.parse("show ntp associations")
        if "peer" not in self.ntp_associations:
            # table.add_row(f"{self.device.name}", "[red]FAILED[/red]")
            # with console.capture() as capture:
            #     console.print(table)
            # table_str = capture.get()
            # log.info(table_str)
            self.failed(f"show_ntp_associations for {self.device.name} FAILED")
        # else:
        #     table.add_row(f"{self.device.name}", "[green]PASSED[/green]")
        #     with console.capture() as capture:
        #         console.print(table)
        #     table_str = capture.get()
        #     log.info(table_str)

    @aetest.test
    def test_ntp_association_reach(self):
        self.ntp_reach_failed = False
        self.peer_ip_failed_list = []
        for peer_ip, peer_data in self.ntp_associations.get(
            "peer", {}
        ).items():
            for _, mode_data in peer_data.get("local_mode", {}).items():
                # table = Table(
                #     title="NTP Reach Test Results", title_style="bold magenta"
                # )
                # table.add_column("Device", justify="center", style="cyan")
                # table.add_column("NTP Peer", justify="center", style="cyan")
                # table.add_column(
                #     "NTP Reach Threshold", justify="center", style="cyan"
                # )
                # table.add_column(
                #     "NTP Reach Status", justify="center", style="cyan"
                # )
                # table.add_column("Test Status", justify="center", style="cyan")
                reach_value = mode_data.get("reach")
                if reach_value != 377:
                    # table.add_row(
                    #     f"{self.device.name}",
                    #     f"{peer_ip}",
                    #     "==377",
                    #     f"[red]{reach_value}[/red]",
                    #     "[red]FAILED[/red]",
                    # )
                    # with console.capture() as capture:
                    #     console.print(table)
                    # table_str = capture.get()
                    # log.info(table_str)
                    self.ntp_reach_failed = True
                    self.peer_ip_failed_list.append(peer_ip)
                # else:
                #     table.add_row(
                #         f"{self.device.name}",
                #         f"{peer_ip}",
                #         "==377",
                #         f"[green]{reach_value}[/green]",
                #         "[green]PASSED[/green]",
                #     )
                #     with console.capture() as capture:
                #         console.print(table)
                #     table_str = capture.get()
                #     log.info(table_str)
        if self.ntp_reach_failed is True:
            self.failed_peers = ", ".join(self.peer_ip_failed_list)
            self.failed(
                "test_ntp_association_reach FAILED for "
                f"{self.device.name} on peers {self.failed_peers}"
            )

    @aetest.test
    def test_ntp_association_clock_state(self):
        # table = Table(
        #     title="NTP Associations Clock State", title_style="bold magenta"
        # )
        # table.add_column("Device", justify="center", style="cyan")
        # table.add_column(
        #     "NTP Expected Clock State", justify="center", style="cyan"
        # )
        # table.add_column(
        #     "NTP Actual Clock State", justify="center", style="cyan"
        # )
        # table.add_column("Test Status", justify="center", style="cyan")
        ntp_clock_state = (
            self.ntp_associations["clock_state"]
            .get("system_status")
            .get("clock_state")
        )
        if ntp_clock_state is not None and ntp_clock_state != "synchronized":
            # table.add_row(
            #     f"{self.device.name}",
            #     "synchronized",
            #     f"[red]{ntp_clock_state}[/red]",
            #     "[red]FAILED[/red]",
            # )
            # with console.capture() as capture:
            #     console.print(table)
            # table_str = capture.get()
            # log.info(table_str)
            self.failed(
                "test_ntp_association_clock_state for "
                f"{self.device.name} FAILED"
            )
        # else:
        #     table.add_row(
        #         f"{self.device.name}",
        #         "synchronized",
        #         f"[green]{ntp_clock_state}[/green]",
        #         "[green]PASSED[/green]",
        #     )
        #     with console.capture() as capture:
        #         console.print(table)
        #     table_str = capture.get()
        #     log.info(table_str)


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        testbed.disconnect()


if __name__ == "__main__":
    aetest.main
