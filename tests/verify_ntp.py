import logging
import os
import yaml
from rich.console import Console
from rich.table import Table
from pyats import aetest
from pyats.log.utils import banner


log = logging.getLogger(__name__)
log.info(banner("pyATS TDD Automated Network Testing"))

console = Console()

WORKING_DIR = "/home/rickey/Scripts/python/pyats/"


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
        table = Table(
            title="Show NTP Associations Test", title_style="bold magenta"
        )
        table.add_column("Device", justify="center", style="cyan")
        table.add_column("Test Status", justify="center", style="cyan")
        self.ntp_associations = self.device.parse("show ntp associations")
        if "peer" not in self.ntp_associations:
            table.add_row(f"{self.device.name}", "[red]FAILED[/red]")
            with console.capture() as capture:
                console.print(table)
            table_str = capture.get()
            log.info(table_str)
            self.failed(f"show_ntp_associations for {self.device.name} FAILED")
        else:
            table.add_row(f"{self.device.name}", "[green]PASSED[/green]")
            with console.capture() as capture:
                console.print(table)
            table_str = capture.get()
            log.info(table_str)

    @aetest.test
    def test_ntp_association_reach(self):
        self.ntp_reach_failed = False
        self.peer_ip_failed_list = []
        for peer_ip, peer_data in self.ntp_associations.get(
            "peer", {}
        ).items():
            for _, mode_data in peer_data.get("local_mode", {}).items():
                table = Table(
                    title="NTP Reach Test Results", title_style="bold magenta"
                )
                table.add_column("Device", justify="center", style="cyan")
                table.add_column("NTP Peer", justify="center", style="cyan")
                table.add_column(
                    "NTP Reach Threshold", justify="center", style="cyan"
                )
                table.add_column(
                    "NTP Reach Status", justify="center", style="cyan"
                )
                table.add_column("Test Status", justify="center", style="cyan")
                reach_value = mode_data.get("reach")
                if reach_value != 377:
                    table.add_row(
                        f"{self.device.name}",
                        f"{peer_ip}",
                        "==377",
                        f"[red]{reach_value}[/red]",
                        "[red]FAILED[/red]",
                    )
                    with console.capture() as capture:
                        console.print(table)
                    table_str = capture.get()
                    log.info(table_str)
                    self.ntp_reach_failed = True
                    self.peer_ip_failed_list.append(peer_ip)
                else:
                    table.add_row(
                        f"{self.device.name}",
                        f"{peer_ip}",
                        "==377",
                        f"[green]{reach_value}[/green]",
                        "[green]PASSED[/green]",
                    )
                    with console.capture() as capture:
                        console.print(table)
                    table_str = capture.get()
                    log.info(table_str)
        if self.ntp_reach_failed is True:
            self.failed_peers = ", ".join(self.peer_ip_failed_list)
            self.failed(
                "test_ntp_association_reach FAILED for "
                f"{self.device.name} on peers {self.failed_peers}"
            )

    @aetest.test
    def test_ntp_association_clock_state(self):
        table = Table(
            title="NTP Associations Clock State", title_style="bold magenta"
        )
        table.add_column("Device", justify="center", style="cyan")
        table.add_column(
            "NTP Expected Clock State", justify="center", style="cyan"
        )
        table.add_column(
            "NTP Actual Clock State", justify="center", style="cyan"
        )
        table.add_column("Test Status", justify="center", style="cyan")
        ntp_clock_state = (
            self.ntp_associations["clock_state"]
            .get("system_status")
            .get("clock_state")
        )
        if ntp_clock_state is not None and ntp_clock_state != "synchronized":
            table.add_row(
                f"{self.device.name}",
                "synchronized",
                f"[red]{ntp_clock_state}[/red]",
                "[red]FAILED[/red]",
            )
            with console.capture() as capture:
                console.print(table)
            table_str = capture.get()
            log.info(table_str)
            self.failed(
                f"test_ntp_association_clock_state for {self.device.name} FAILED"
            )
        else:
            table.add_row(
                f"{self.device.name}",
                "synchronized",
                f"[green]{ntp_clock_state}[/green]",
                "[green]PASSED[/green]",
            )
            with console.capture() as capture:
                console.print(table)
            table_str = capture.get()
            log.info(table_str)

    @aetest.test
    def save_show_ntp_association_json(self):
        try:
            self.json_dir = os.path.join(WORKING_DIR, "json/")
            if not os.path.exists(self.json_dir):
                os.mkdir(self.json_dir, mode=0o775)
            self.filename = os.path.join(
                self.json_dir, f"show_ntp_associations_{self.device.name}.json"
            )
            self.device.api.save_dict_to_json_file(
                data=list(self.ntp_associations.values()),
                filename=self.filename,
            )
        except Exception:
            self.failed("save_show_ntp_association_json FAILED")

    @aetest.test
    def save_show_ntp_association_yaml(self):
        try:
            self.yaml_dir = os.path.join(WORKING_DIR, "yaml/")
            if not os.path.exists(self.yaml_dir):
                os.mkdir(self.yaml_dir, mode=0o775)
            self.filename = os.path.join(
                self.yaml_dir, f"show_ntp_associations_{self.device.name}.yaml"
            )
            with open(self.filename, "w") as f:
                f.write(
                    yaml.dump(self.ntp_associations, default_flow_style=False)
                )
        except Exception:
            self.failed("save_show_ntp_association_yaml FAILED")

    @aetest.test
    def save_show_ntp_association_csv(self):
        try:
            jinja_dir = os.path.join(WORKING_DIR, "jinja/")
            self.show_ntp_association_csv = (
                self.device.api.load_jinja_template(
                    path=jinja_dir,
                    file="ntp_association_json_to_csv.j2",
                    data=self.ntp_associations,
                )
            )
            self.csv_dir = os.path.join(WORKING_DIR, "csv/")
            if not os.path.exists(self.csv_dir):
                os.mkdir(self.csv_dir, mode=0o775)
            self.filename = os.path.join(
                self.csv_dir, f"show_ntp_associations_{self.device.name}.csv"
            )
            with open(self.filename, "w") as f:
                f.write(self.show_ntp_association_csv)
        except Exception:
            self.failed("save_show_ntp_association_csv FAILED")

    # @aetest.test
    # def save_show_ntp_association_md(self):
    # try:
    # jinja_dir = os.path.join(WORKING_DIR, "jinja/")
    # self.show_ntp_association_md = \
    # self.device.api.load_jinja_template(
    # path=jinja_dir,
    # file="ntp_association_json_to_md.j2",
    # data=self.ntp_associations)
    # self.md_dir = os.path.join(WORKING_DIR, "md/")
    # if not os.path.exists(self.md_dir):
    # os.mkdir(self.md_dir, mode=0o775)
    # self.filename = os.path.join(self.md_dir,
    # "show_ntp_associations_"
    # f"{self.device.name}"
    # ".md")
    # with open(self.filename, "w") as f:
    # f.write(self.show_ntp_association_md)
    # except Exception:
    # self.failed("save_show_ntp_association_md FAILED")


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        testbed.disconnect()


if __name__ == "__main__":
    aetest.main
