from pyats import aetest
from genie.metaparser.util.exceptions import (
    SchemaMissingKeyError,
    SchemaEmptyParserError,
)


class TestIpRouteBgp(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed, device_name):
        self.device = testbed.devices[device_name]

        try:
            parsed_output = self.device.parse("show ip route bgp")
        except SchemaEmptyParserError, SchemaMissingKeyError:
            self.failed(f"{self.device.name}: no BGP up route table")

        self.routes = parsed_output["vrf"]["default"]["address_family"][
            "ipv4"
        ]["routes"]

    @aetest.test
    def test_bgp_session_state(self):
        if "10.2.254.3/32" in list(self.routes):
            self.failed(
                f"{self.device.name}: 10.2.254.3/32 still in routing table"
            )
