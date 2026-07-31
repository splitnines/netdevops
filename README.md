# NetDevOps Pipeline

## Overview

This repository defines a Git-based workflow for applying and validating network changes on Cisco IOS XE devices. Ansible performs configuration backup and deployment, while pyATS performs post-deployment validation. GitHub Actions runs the workflow on a self-hosted runner that has access to the target network.

The repository is modular. A change may provide an optional backup playbook, one or more deployment playbooks, optional pyATS tests, or any combination of these units. Inventory data, Ansible variables, pyATS testbeds, test suites, and individual test scripts are maintained as separate files so that they can be replaced or extended for a specific environment.

Pipeline execution is ordered as follows:

1. Validate Ansible playbook syntax.
2. Back up device configurations when `playbooks/config_backup.yml` exists.
3. Run deployment playbooks from the top level of `playbooks/`.
4. Run pyATS tests when `tests/job.py` exists.

The jobs run serially. A failed job prevents dependent jobs from running.

## Repository layout

```text
.
├── .github/workflows/ci-cd.yml   # GitHub Actions workflow
├── ansible.cfg                    # Ansible defaults and connection settings
├── backups/                       # Configuration backups
├── inventory/
│   ├── group_vars/                # Variables organized by inventory group
│   └── library/                   # Alternate and reference inventories
├── playbooks/
│   └── library/                   # Reusable playbook examples
├── tests/
│   ├── config/testbeds/           # pyATS testbed definitions
│   ├── library/                   # Example job files
│   ├── test_suites/               # Suites and their test scripts
│   └── unit_tests/                # Python unit tests
├── pyproject.toml                 # Python project and dependency definitions
└── uv.lock                        # Locked Python dependency versions
```

Files under `playbooks/library/` and `tests/libary/` are examples. The pipeline executes playbooks placed directly under `playbooks/` and executes the job at `tests/job.py`.

## Prerequisites

- Git
- [`uv`](https://docs.astral.sh/uv/)
- SSH access to the GitHub repository
- Access to the network devices defined by the selected inventory or pyATS testbed
- Valid device credentials

The project requires Python 3.14 or later, as specified in `pyproject.toml`.

## Clone and initialize the environment

Clone the repository and change to its root directory:

```bash
git clone git@github.com:splitnines/netdevops.git
cd netdevops
```

Install Python 3.14 and synchronize the virtual environment from `pyproject.toml` and `uv.lock`:

```bash
uv python install 3.14
uv sync --locked --python 3.14
```

Commands can be run in the managed environment with `uv run`. Activating `.venv` is not required. If direct command execution is preferred, activate it with:

```bash
source .venv/bin/activate
```

Install the Ansible collections declared in `requirements.yml` if they are not already available:

```bash
uv run ansible-galaxy collection install -r requirements.yml
```

## Change workflow

### 1. Create a branch

Start from the current `main` branch and create a branch for the proposed network change:

```bash
git switch main
git pull --ff-only origin main
git switch -c change/<change-name>
```

Do not perform deployment work directly on `main`. The GitHub Actions workflow excludes pushes to `main`.

### 2. Configure Ansible

#### Credentials

The included group variables read credentials from `CISCO_USER` and `CISCO_PASS`. Export them for local execution:

```bash
export CISCO_USER='<username>'
export CISCO_PASS='<password>'
```

Do not commit credentials. The GitHub Actions runner obtains these values from repository secrets with the same names.

#### Inventory and group variables

`inventory/inventory.yml` is the canonical Ansible inventory for every pipeline stage and local Ansible command. It must be the only inventory file stored directly under `inventory/`.

Store alternate or reference inventory files under `inventory/library/`. To use one, copy it to the canonical path and modify the copy as required. For example:

```bash
cp inventory/library/<source-inventory>.yml inventory/inventory.yml
```

Do not configure a pipeline stage to use an inventory file from `inventory/library/`. Keeping a single execution path ensures that syntax validation, configuration backup, and deployment target the same devices and groups.

Define shared variables under `inventory/group_vars/`. Ensure that inventory group names match the corresponding group-variable filenames and the `hosts` values in each playbook.

Verify the canonical inventory before running a playbook or pushing the branch:

```bash
uv run ansible-inventory -i inventory/inventory.yml --graph
```

#### Optional backup playbook

To enable configuration backup, create `playbooks/config_backup.yml` or copy the supplied example:

```bash
cp playbooks/library/config_backup.yml playbooks/config_backup.yml
```

The filename is significant: the backup stage checks specifically for `playbooks/config_backup.yml`. The deployment stage excludes files whose names end in `config_backup.yml`.

Validate and, when appropriate, run the backup locally:

```bash
uv run ansible-playbook --syntax-check \
  -i inventory/inventory.yml playbooks/config_backup.yml
uv run ansible-playbook \
  -i inventory/inventory.yml playbooks/config_backup.yml
```

Generated `*.cfg` backup files are ignored by Git and must not be committed.

#### Deployment playbooks

Create or copy each deployment playbook into the top level of `playbooks/`. For example:

```bash
cp playbooks/library/ntp_config.yml playbooks/ntp_config.yml
```

The deployment stage finds all `.yml` and `.yaml` files directly under `playbooks/`, sorts them by filename, and executes them in that order. It does not recursively execute files under `playbooks/library/`. Use filename prefixes when execution order matters.

Validate each deployment playbook before committing it:

```bash
uv run ansible-playbook --syntax-check \
  -i inventory/inventory.yml playbooks/ntp_config.yml
```

Run a playbook locally only when its effect and target inventory have been reviewed:

```bash
uv run ansible-playbook \
  -i inventory/inventory.yml playbooks/ntp_config.yml
```

### 3. Configure pyATS (optional)

The pyATS stage is enabled only when `tests/job.py` exists. Create that file or copy and modify an example from `tests/library/`:

```bash
cp tests/library/job.py tests/job.py
```

Configure the job's testbed and suite paths for the target environment. Testbed files belong under `tests/config/testbeds/` and may reference `CISCO_USER` and `CISCO_PASS` from the environment.

The pyATS execution hierarchy is:

1. `tests/job.py` is the pipeline entry point.
2. The job loads a testbed and invokes a test suite from `tests/test_suites/`.
3. The test suite imports and runs one or more test scripts, conventionally stored under `tests/test_suites/test_scripts/`.

A typical layout is:

```text
tests/
├── job.py
├── config/testbeds/<testbed>.yaml
└── test_suites/
    ├── <suite>_test_suite.py
    └── test_scripts/
        └── <feature>/<test_script>.py
```

Run the same pyATS command used by the pipeline:

```bash
uv run pyats run job tests/job.py --no-mail --no-archive
```

Remove `tests/job.py` when pyATS validation is not required for a change.

### 4. Review and commit the change

Review all modified and untracked files before staging them:

```bash
git status
git diff
```

Stage only the files required for the change, then create a local commit:

```bash
git add inventory/ playbooks/ tests/
git commit -m "Describe the network change"
```

Do not use `git add .` without first verifying that no credentials, generated output, or unrelated files will be included.

### 5. Push the branch

Push the branch and set its upstream reference:

```bash
git push --set-upstream origin change/<change-name>
```

## GitHub Actions execution and status

The workflow is defined in `.github/workflows/ci-cd.yml` and runs on a self-hosted GitHub Actions worker. GitHub displays the worker state and the result of each pipeline job under the repository's **Actions** page and on the associated commit or pull request.

The reported jobs are:

- **Validate**: synchronizes the Python environment and syntax-checks top-level playbooks.
- **Backup**: runs `playbooks/config_backup.yml` when present; otherwise its operational steps are skipped.
- **Deploy**: executes top-level deployment playbooks in sorted order.
- **Tests**: runs `tests/job.py` when present; otherwise its operational steps are skipped.

Each job is reported as queued, in progress, successful, failed, cancelled, or skipped. Inspect the step logs for command output and failure details. Because the workflow uses `needs`, Backup depends on Validate, Deploy depends on Backup, and Tests depends on Deploy.

Automatic runs currently apply to non-`main` pushes that modify `playbooks/**` or `test/**`, as configured in the workflow. The configured path is `test/**` (singular), while this repository stores pyATS content under `tests/**` (plural). A branch containing only changes under `tests/**` will therefore not start the workflow automatically. Start such a run manually with **Actions > NetDevOps CI/CD > Run workflow**, or include an applicable playbook change. Manual execution is available through `workflow_dispatch`.
