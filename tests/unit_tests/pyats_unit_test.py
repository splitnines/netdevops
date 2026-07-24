import json
import os
from test_suites.test_scripts.eigrp.ipv6_interfaces_test import (
    extract_eigrp_intf_metrics,
)
from test_suites.test_scripts.ospfv2.ip_protocols import extract_ospf_rid


def test_extract_eigrp_intf_metrics():
    input_test_data = os.path.join(
        os.path.dirname(__file__), "data", "eigrp_instances.json"
    )

    with open(input_test_data, "r") as f:
        data = json.load(f)

    results = list(extract_eigrp_intf_metrics(data))

    assert results == [
        (
            "65001",
            "Ethernet0/1",
            {
                "peers": 1,
                "xmit_q_unreliable": 0,
                "xmit_q_reliable": 0,
                "peer_q_unreliable": 0,
                "peer_q_reliable": 0,
                "mean_srtt": 1,
                "pacing_time_unreliable": 0,
                "pacing_time_reliable": 2,
                "mcast_flow_timer": 50,
                "pend_routes": 0,
            },
        ),
        (
            "65001",
            "Ethernet0/0",
            {
                "peers": 1,
                "xmit_q_unreliable": 0,
                "xmit_q_reliable": 0,
                "peer_q_unreliable": 0,
                "peer_q_reliable": 0,
                "mean_srtt": 2,
                "pacing_time_unreliable": 0,
                "pacing_time_reliable": 2,
                "mcast_flow_timer": 50,
                "pend_routes": 0,
            },
        ),
    ]


def test_extract_ospf_rid():
    input_test_data = os.path.join(
        os.path.dirname(__file__), "data", "ip_protocols_ospf.json"
    )

    with open(input_test_data, "r") as f:
        data = json.load(f)

    results = list(extract_ospf_rid(data["protocols"]["ospf"]))

    assert results[0] == {
        "vrf": "default",
        "addresss_family": "ipv4",
        "instance": "1",
        "router_id": "2.2.2.2",
    }
