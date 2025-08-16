SHELL := /bin/bash

build:
	docker compose build

# writes testbed/testbed.yaml from .env + j2 template
render:
	docker compose run --rm pyats python tools/render_testbed.py

shell:
	docker compose run --rm pyats bash

test: render
	docker compose run --rm pyats pytest -q

# example: plan/apply hostname change on r1
DEVICES ?= r1 sw2-1
DESCRIPTION ?= configured via pipeline

plan-loopback0-all: render
	docker compose run --rm pyats bash -lc '\
	  set -euo pipefail; \
	  for d in $(DEVICES); do \
	    echo "== PLAN $$d =="; \
	    python tools/push_config.py --device "$$d" \
	      --template configs/loopback_desc.j2 \
	      --vars description="$(DESCRIPTION)" \
	      --plan; \
	    echo; \
	  done'

apply-loopback0-all: render
	docker compose run --rm pyats bash -lc '\
	  set -euo pipefail; \
	  for d in $(DEVICES); do \
	    echo "== APPLY $$d =="; \
	    python tools/push_config.py --device "$$d" \
	      --template configs/loopback_desc.j2 \
	      --vars description="$(DESCRIPTION)" \
	      --apply; \
	    echo; \
	  done'
