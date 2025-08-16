from unicon.core.errors import ConnectionError
from genie.testbed import load
from jinja2 import Template
from pathlib import Path
import sys
import argparse

# !/usr/bin/env python3


def render_config(tmpl_path: Path, **vars_) -> str:
    text = tmpl_path.read_text()
    return Template(text).render(**vars_).strip()


def main():
    ap = argparse.ArgumentParser(
        description="Plan/apply config to a device via pyATS/Unicon"
    )
    ap.add_argument(
        "--device", required=True, help="device name in testbed (e.g., r1)"
    )
    ap.add_argument("--template", required=True, help="Jinja2 template path")
    ap.add_argument(
        "--vars", nargs="*", default=[], help="key=value pairs for template"
    )
    ap.add_argument(
        "--plan", action="store_true", help="show what will be sent"
    )
    ap.add_argument(
        "--apply", action="store_true", help="send config to device"
    )
    args = ap.parse_args()

    if not (args.plan or args.apply):
        print("Use --plan and/or --apply", file=sys.stderr)
        sys.exit(2)

    kv = {}
    for pair in args.vars:
        if "=" not in pair:
            print(f"Bad var '{pair}', expected key=value", file=sys.stderr)
            sys.exit(2)
        k, v = pair.split("=", 1)
        kv[k] = v

    tb = load("testbed/testbed.yaml")
    dev = tb.devices[args.device]
    try:
        dev.connect(log_stdout=False)
    except ConnectionError as e:
        print(f"Failed to connect: {e}", file=sys.stderr)
        sys.exit(1)

    cfg = render_config(Path(args.template), **kv)
    if not cfg:
        print("Template rendered empty config, nothing to do.")
        return 0

    print("=== CANDIDATE CONFIG ===")
    print(cfg)
    print("========================")

    if args.apply:
        print("[+] Applying configuration...")
        # send in config mode
        dev.configure(cfg)
        print("[+] Done.")

    if dev.is_connected():
        dev.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
