# NetDevOps Pipeline

## Overview

This repository defines a local Git-driven workflow for applying and validating network changes on Cisco IOS XE devices. Ansible performs syntax validation, configuration backup, and deployment. pyATS performs optional post-deployment validation.

The pipeline runs through Git `pre-commit` and `post-commit` hooks installed in each local clone. Commits on `main` and commits made from a detached `HEAD` skip the pipeline. A commit on any other branch runs the pre-commit pipeline before Git creates the commit and the post-commit pipeline after Git creates it.

The repository is modular. A change may include an optional backup playbook, one or more deployment playbooks, optional pyATS tests, or any combination of these units. Inventory data, Ansible variables, pyATS testbeds, test suites, and individual test scripts are maintained separately so that each can be replaced or extended for a specific environment.

## Pipeline sequence

For a commit on a branch other than `main`, the local pipeline executes in this order:

1. The `pre-commit` hook synchronizes the Python environment with `uv`.
2. The pre-commit pipeline syntax-checks top-level Ansible playbooks.
3. The pre-commit pipeline runs an optional backup playbook.
4. Git creates the commit if the pre-commit pipeline succeeds.
5. The `post-commit` hook runs top-level deployment playbooks.
6. The post-commit pipeline runs pyATS when `tests/job.py` exists.

A pre-commit pipeline failure prevents Git from creating the commit. A post-commit failure cannot remove or roll back a commit that Git has already created.

## Repository layout

```text
.
├── ansible.cfg                    # Ansible defaults and connection settings
├── backups/                       # Configuration backups
├── inventory/
│   ├── inventory.yml              # Canonical inventory; update for the target environment
│   └── group_vars/
│       └── all_devices.yml        # Shared variables for all managed devices
├── local-pipeline/
│   ├── pre-commit                 # Git pre-commit hook source
│   ├── post-commit                # Git post-commit hook source
│   ├── local_ci-cd-pre            # Pre-commit pipeline implementation
│   └── local_ci-cd-post           # Post-commit pipeline implementation
├── playbooks/
│   └── library/                   # Reusable playbook examples
├── tests/
│   ├── config/testbeds/           # pyATS testbed definitions
│   ├── library/                   # Example job files
│   ├── test_suites/               # Suites and test scripts
│   └── unit_tests/                # Python unit tests
├── pyproject.toml                 # Python project and dependency definitions
└── uv.lock                        # Locked Python dependency versions
```

Files under `playbooks/library/` and `tests/library/` are reference files. The pipeline executes playbooks placed directly under `playbooks/`, uses `inventory/inventory.yml`, and executes the pyATS job at `tests/job.py`.

## Prerequisites

- Git
- Bash
- [`uv`](https://docs.astral.sh/uv/)
- Access to the network devices defined by the active Ansible inventory or pyATS testbed
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

Commands can be run in the managed environment with `uv run`. Activating `.venv` is not required. To run commands directly from the environment, activate it with:

```bash
source .venv/bin/activate
```

Install the Ansible collections declared in `requirements.yml` if they are not already available:

```bash
uv run ansible-galaxy collection install -r requirements.yml
```

## Install the local Git hooks

Git does not install repository hooks when cloning a repository. Each local clone must copy the hook files from `local-pipeline/` into `.git/hooks/`. These commands replace hooks with the same names, so inspect or back up existing hooks first.

```bash
cp local-pipeline/pre-commit .git/hooks/pre-commit
cp local-pipeline/post-commit .git/hooks/post-commit
chmod +x .git/hooks/pre-commit .git/hooks/post-commit
```

The hooks call `local-pipeline/local_ci-cd-pre` and `local-pipeline/local_ci-cd-post` from the working tree. Confirm that all four files are executable:

```bash
test -x .git/hooks/pre-commit
test -x .git/hooks/post-commit
test -x local-pipeline/local_ci-cd-pre
test -x local-pipeline/local_ci-cd-post
```

Each command exits with status zero when the corresponding file is executable. Recopy the hooks after pulling changes to `local-pipeline/pre-commit` or `local-pipeline/post-commit`.

The installed hooks operate as follows:

- They run for commits on any named branch except `main`.
- They skip execution when `HEAD` is detached.
- They run synchronously in the terminal that executes `git commit`.
- They expect the tracked pipeline scripts to remain under `local-pipeline/`.
- They operate on the current working tree rather than an isolated checkout; unstaged changes can therefore affect pipeline execution.
- They use the credentials and network access available to the local user running Git.

## Change workflow

### 1. Create a branch

Start from the current `main` branch and create a branch for the proposed network change:

```bash
git switch main
git pull --ff-only origin main
git switch -c change/<change-name>
```

The hooks intentionally skip commits made on `main`. Perform pipeline work on a separate branch.

### 2. Configure credentials

The included Ansible group variables and pyATS testbeds read credentials from `CISCO_USER` and `CISCO_PASS`. Export them in the shell before committing or running pipeline commands:

```bash
export CISCO_USER='<username>'
export CISCO_PASS='<password>'
```

Do not commit credentials. The hooks inherit environment variables from the process that runs `git commit`.

### 3. Configure the Ansible inventory

`inventory/inventory.yml` is the canonical and only Ansible inventory used by the local pipeline and manual Ansible commands. Update this file directly for the target environment before committing a change.

Define the required device groups and hosts in `inventory/inventory.yml`. For each host, set the appropriate management address and any host-specific connection values. Ensure that group names match the `hosts` values used by the playbooks.

`inventory/group_vars/all_devices.yml` contains connection settings, credential lookups, and other variables shared by all managed devices. Keep every managed device in the `all_devices` inventory group so that these variables apply consistently. Update this file only when the shared settings for the environment need to change. Credentials must continue to use the `CISCO_USER` and `CISCO_PASS` environment variables rather than literal values committed to the repository.

Review the resulting host and group hierarchy before committing:

```bash
uv run ansible-inventory -i inventory/inventory.yml --graph
```

Display the resolved variables for a specific device when validating inventory behavior:

```bash
uv run ansible-inventory -i inventory/inventory.yml \
  --host <device-name>
```

### 4. Configure an optional backup playbook

The pre-commit pipeline searches the top level of `playbooks/` for the first `.yml` or `.yaml` file whose name begins with `config_backup`. To enable configuration backup, create a matching playbook or copy an example:

```bash
cp playbooks/library/config_backup.yml playbooks/config_backup.yml
```

Names such as `config_backup.yml` and `config_backup_consoles.yml` are recognized. Backup playbooks are excluded from post-commit deployment.

The backup runs before Git creates the commit and uses `inventory/inventory.yml`. A backup failure stops the commit. Generated `*.cfg` files under `backups/` are ignored by Git and must not be committed.

To test a backup playbook explicitly:

```bash
uv run ansible-playbook --syntax-check \
  -i inventory/inventory.yml playbooks/config_backup.yml
uv run ansible-playbook \
  -i inventory/inventory.yml playbooks/config_backup.yml
```

### 5. Configure deployment playbooks

Create or copy deployment playbooks into the top level of `playbooks/`:

```bash
cp playbooks/library/configuration_template.yml \
  playbooks/configuration.yml
```

The post-commit pipeline processes top-level `.yml` and `.yaml` files. Files with names containing `config_backup` are skipped. Playbooks under `playbooks/library/` are not executed.

All deployment playbooks use `inventory/inventory.yml`. Review the active inventory and the effect of every playbook before committing because deployment begins after the commit is created.

Validate a playbook manually when needed:

```bash
uv run ansible-playbook --syntax-check \
  -i inventory/inventory.yml playbooks/configuration.yml
```

### 6. Configure pyATS (optional)

The post-commit pipeline runs pyATS only when `tests/job.py` exists. Create that file or copy and modify the example from `tests/library/`:

```bash
cp tests/library/job.py tests/job.py
```

Configure the job's testbed and suite paths for the target environment. Testbed files belong under `tests/config/testbeds/` and may reference `CISCO_USER` and `CISCO_PASS` from the environment.

The pyATS execution hierarchy is:

1. `tests/job.py` is the pipeline entry point.
2. The job loads a testbed and invokes a test suite from `tests/test_suites/`.
3. The test suite imports and runs one or more test scripts from `tests/test_suites/test_scripts/`.

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

Run the same pyATS command used by the post-commit pipeline:

```bash
uv run pyats run job tests/job.py --no-mail --no-archive
```

Remove `tests/job.py` when pyATS validation is not required.

### 7. Review and commit the change

Review all modified and untracked files before staging them:

```bash
git status
git diff
```

Stage only the required files:

```bash
git add inventory/ playbooks/ tests/
```

Create the commit:

```bash
git commit -m "Describe the network change"
```

The pre-commit hook runs before the commit is created. If it succeeds, Git creates the commit and invokes the post-commit hook. Both hooks print pipeline progress to the terminal.

Do not use `git add .` without verifying that no credentials, generated output, or unrelated files will be included.

### 8. Review pipeline results

The pipeline writes timestamped command output under `logs/`:

- `logs/ansible-pre-cicd-*.log` contains pre-commit Ansible syntax-check and backup output.
- `logs/ansible-post-cicd-*.log` contains post-commit Ansible deployment output.
- `logs/pyats-post-cicd-*.log` contains post-commit pyATS output.

The scripts also report progress and completion status in the terminal. Inspect the applicable log when a stage reports a failure.

The current pre-commit implementation enters its general syntax-check stage only when at least one top-level `.yml` or `.yaml` playbook exists. Once that condition is met, the syntax-check command includes both `.yml` and `.yaml` files.

The current post-commit implementation records a pyATS failure in its log and terminal output but does not return that failure as the final pipeline exit status. An Ansible deployment failure exits the post-commit pipeline with a nonzero status, but the existing commit remains in local history because post-commit hooks run after commit creation.

### 9. Push the change branch

After reviewing the commit and local pipeline results, confirm the current branch and working-tree status:

```bash
git branch --show-current
git status
```

Push the change branch to `origin` and configure its upstream tracking branch:

```bash
git push --set-upstream origin change/<change-name>
```

Replace `change/<change-name>` with the actual local branch name. After the upstream is configured, subsequent commits can be pushed with:

```bash
git push
```

Pushing does not invoke the local `pre-commit` or `post-commit` hooks. Those hooks run only when a local commit is created.
