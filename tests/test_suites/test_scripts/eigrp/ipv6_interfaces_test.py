from pyats import aetest
from genie.metaparser.util.exceptions import (
    SchemaMissingKeyError,
    SchemaEmptyParserError,
)


def extract_eigrp_intf_metrics(eigrp_instances):
    for asn, eigrp_instance in eigrp_instances.items():
        interfaces = eigrp_instance["address_family"]["ipv6"]["interface"]

        for interface_name, metrics in interfaces.items():
            yield asn, interface_name, metrics


class TestEigrpV6Interfaces(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed, device_name):
        self.device = testbed.devices[device_name]

        try:
            parsed_output = self.device.parse("show ipv6 eigrp interfaces")
        except SchemaEmptyParserError, SchemaMissingKeyError:
            self.failed(
                f"{self.device.name}: no EIGRP interface data returned"
            )

        self.eigrp_interfaces = parsed_output["vrf"]["default"][
            "eigrp_instance"
        ]

    @aetest.test
    def test_eigrp_peer_count(self):
        failures = []

        for asn, interface_name, metrics in extract_eigrp_intf_metrics(
            self.eigrp_interfaces
        ):
            if metrics["peers"] < 1:
                failures.append(f"{interface_name} (AS {asn})")

        if failures:
            self.failed(
                f"{self.device.name}: no peers on {', '.join(failures)}"
            )

    @aetest.test
    def test_eigrp_xmit_queue(self):
        failures = []

        for asn, interface_name, metrics in extract_eigrp_intf_metrics(
            self.eigrp_interfaces
        ):
            if (
                metrics["xmit_q_unreliable"] > 0
                or metrics["xmit_q_reliable"] > 0
            ):
                failures.append(f"{interface_name}, (AS {asn})")

        if failures:
            self.failed(
                f"{self.device.name}: xmit_q issues on {', '.join(failures)}"
            )
