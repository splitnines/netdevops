from pyats import aetest
from genie.metaparser.util.exceptions import (
    SchemaMissingKeyError,
    SchemaEmptyParserError,
)

OSPF_RIDS = []


def extract_ospf_rid(ip_protocols_ospf):
    try:
        results = []
        for vrf, vrf_data in ip_protocols_ospf["vrf"].items():
            for address_family, af_data in vrf_data["address_family"].items():
                for instance, instance_data in af_data["instance"].items():
                    results.append(
                        {
                            "vrf": vrf,
                            "addresss_family": address_family,
                            "instance": instance,
                            "router_id": instance_data["router_id"],
                        }
                    )

        return results
    except ValueError as e:
        raise ValueError(f"Missing required OSPF field: {e}")


class TestIpv4ProtocolsOspf(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed, device_name):
        self.device = testbed.devices[device_name]

        try:
            parsed_output = self.device.parse("show ip protocols")
            self.ip_protocols_ospf = parsed_output["protocols"]["ospf"]
        except SchemaEmptyParserError, SchemaMissingKeyError:
            self.failed(f"{self.device.name}: no ospf in ip protocols")
            return

        failures = []

        try:
            results = extract_ospf_rid(self.ip_protocols_ospf)
        except ValueError as e:
            failures.append(f"{self.device.name}: {e}")

        for result in results:
            OSPF_RIDS.append(result)

        if failures:
            self.failed(f"{', '.join(failures)}")


class TestDuplicateOspfRids(aetest.Testcase):
    @aetest.test
    def test_check_duplicate_rids(self):
        duplicates = []
        for n, router_id in enumerate(OSPF_RIDS):
            if router_id in OSPF_RIDS[:n] and router_id not in duplicates:
                duplicates.append(router_id)

        if len(duplicates) > 0:
            self.failed(f"duplicate RIDs: {duplicates}")
