from pyats import aetest
from genie.metaparser.util.exceptions import (
    SchemaMissingKeyError,
    SchemaEmptyParserError,
    InvalidCommandError,
)


class TestShowInterfaceDesc(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed, device_name):
        self.device = testbed.devices[device_name]

        try:
            parsed_output = self.device.parse("show interface description")
        except (
            SchemaEmptyParserError,
            SchemaMissingKeyError,
            InvalidCommandError,
        ):
            self.failed(f"{self.device.name}: no interface data returned")

        self.interfaces = parsed_output.get("interfaces")

    @aetest.test
    def test_interface_ethernet00(self):
        intf_desc = "configured by netdevops"
        intf_name = "Ethernet0/0"

        failures = []

        for interface, interface_state in self.interfaces.items():
            if interface == "Ethernet0/0":
                if interface_state.get("description") != intf_desc:
                    failures.append(
                        f"{self.device.name}, interface {intf_name}"
                        "has an incorrect description"
                    )

        if failures:
            self.failed(f"{', '.join(failures)}")
