#!/usr/bin/env python3
import os
import sys
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.dirname(__file__))
tmpl_dir = os.path.join(ROOT, "testbed")
out_path = os.path.join(tmpl_dir, "testbed.yaml")
inv_path = os.path.join(ROOT, "inventory", "devices.yaml")

with open(inv_path, "r") as f:
    inv = yaml.safe_load(f)

env = Environment(loader=FileSystemLoader(tmpl_dir), autoescape=False)
tmpl = env.get_template("testbed.yaml.j2")
rendered = tmpl.render(env=os.environ, inventory=inv)

with open(out_path, "w") as f:
    f.write(rendered)

print(f"[+] Wrote {out_path} from {inv_path}")
