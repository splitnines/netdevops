import os
import yaml
from functools import lru_cache


@lru_cache(None)
def load_inventory():
    here = os.path.dirname(__file__)
    inv = os.path.join(here, "..", "inventory", "devices.yaml")
    with open(inv, "r") as f:
        return yaml.safe_load(f)


def devices_iosxe():
    inv = load_inventory()
    return [d for d in inv["devices"] if d.get("os") == "iosxe"]
