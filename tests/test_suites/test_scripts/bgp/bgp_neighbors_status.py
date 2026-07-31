from pyats import aetest
from genie.metaparser.util.exceptions import (
    SchemaMissingKeyError,
    SchemaEmptyParserError,
)


def extract_bgp_neighbor_session_state(bgp_neighbors):
    for neighbor, neighbor_state in bgp_neighbors.items():
        for af, state in neighbor_state["address_family"].items():
            if af == "ipv4 unicast" or af == "ipv6 unicast":
                yield af, neighbor, state.get("session_state", None)


class TestBgpDefaultNeighborStatus(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed, device_name):
        self.device = testbed.devices[device_name]

        try:
            parsed_output = self.device.parse("show bgp all neighbors")
        except SchemaEmptyParserError, SchemaMissingKeyError:
            self.failed(f"{self.device.name}: no BGP neighbor data returned")

        self.bgp_neighbors = parsed_output["vrf"]["default"]["neighbor"]

    @aetest.test
    def test_bgp_session_state(self):
        failures = []

        for af, neighbor, session_state in extract_bgp_neighbor_session_state(
            self.bgp_neighbors
        ):
            if session_state != "Established":
                failures.append(
                    f"{self.device.name}, {af}, {neighbor}, {session_state}"
                )

        if failures:
            self.failed(
                f"{self.device.name}: BGP Session State Failure "
                f"{', '.join(failures)}"
            )
