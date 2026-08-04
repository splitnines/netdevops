# NetDevOps Pipeline

## Overview

This repository defines a local Git-driven workflow for applying and validating network changes on Cisco IOS XE devices. Ansible performs syntax validation, configuration backup, deployment, configuration rollback and configuration persistence. pyATS performs optional post-deployment validation.

The complete pipeline runs through a Git `pre-commit` hook installed in each local clone. Commits on `main` and commits made from a detached `HEAD` skip the pipeline. On any other branch, Git creates the commit only after every required pipeline stage succeeds. Configuration persistence and rollback are optional capabilities enabled by copying their utility playbooks into `playbooks/utils/`.

The repository is modular. A change may include an optional backup playbook, one or more deployment playbooks, optional pyATS tests, or any combination of these units. Ansible inventory examples contain their associated connection variables, while pyATS testbeds, test suites and individual test scripts remain separate so that each unit can be selected or extended for a specific environment.

## Pipeline sequence

For a commit on a branch other than `main`, the local pipeline executes in this order:

1. Detect one or more `.yml` playbooks directly under `playbooks/`.
2. Install Python 3.14 when necessary and synchronize the environment with `uv`.
3. Syntax-check every top-level `.yml` and `.yaml` playbook.
4. Run the first optional top-level playbook whose filename contains `backup`.
5. If `playbooks/utils/commit_config.yml` exists, run it to save the current running configuration as the rollback baseline.
6. Run each top-level deployment playbook, excluding filenames that contain `backup`.
7. Run pyATS when `tests/job.py` exists.
8. If `playbooks/utils/commit_config.yml` exists, run it again to save the validated configuration.
9. Return control to Git, which creates the commit.

A syntax-check, backup, deployment, pyATS or configuration-save failure rejects the Git commit. When a deployment playbook or pyATS validation fails, the pipeline runs `playbooks/utils/rollback_config.yml` if that file exists. If the rollback utility is not enabled, the pipeline rejects the Git commit without reverting device changes.

## Repository layout

```text
.
├── ansible.cfg                    # Ansible defaults and connection settings
├── backups/                       # Configuration backups
├── inventory/
│   └── library/
│       ├── inventory.yml          # Network CLI inventory example
│       └── inventory_consoles.yml # Console connection inventory example
├── pipeline/
│   ├── pre-commit                 # Git pre-commit hook source
│   └── local_ci-cd-pre            # Complete local pipeline implementation
├── playbooks/
│   ├── library/                   # Reusable playbook examples
│   └── utils/
│       └── library/
│           ├── commit_config.yml  # Save utility template
│           └── rollback_config.yml # Rollback utility template
├── tests/
│   ├── config/testbeds/           # pyATS testbed definitions
│   ├── library/                   # Example job files
│   ├── test_suites/               # Suites and test scripts
│   └── unit_tests/                # Python unit tests
├── pyproject.toml                 # Python project and dependency definitions
└── uv.lock                        # Locked Python dependency versions
```

Files under `inventory/library/`, `playbooks/library/`, `playbooks/utils/library/` and `tests/library/` are reference files. Before running the pipeline, copy and adapt an inventory from `inventory/library/` to `inventory/inventory.yml`. The pipeline executes playbooks placed directly under `playbooks/`, uses the copied `inventory/inventory.yml` and executes the pyATS job at `tests/job.py`. Utility playbooks run only when copied from `playbooks/utils/library/` directly into `playbooks/utils/`.

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

## Install the local Git hook

Git does not install repository hooks when cloning a repository. Each local clone must copy `pipeline/pre-commit` into `.git/hooks/`. This command replaces an existing pre-commit hook, so inspect or back up that file first.

```bash
cp pipeline/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook calls `pipeline/local_ci-cd-pre` from the working tree. Confirm that both files are executable:

```bash
test -x .git/hooks/pre-commit
test -x pipeline/local_ci-cd-pre
```

Each command exits with status zero when the corresponding file is executable. Recopy the hook after pulling changes to `pipeline/pre-commit`.

The installed hook operates as follows:

- It runs for commits on any named branch except `main`.
- It skips execution when `HEAD` is detached.
- It runs synchronously in the terminal that executes `git commit`.
- It expects the tracked implementation to remain at `pipeline/local_ci-cd-pre`.
- It starts the pipeline only when at least one top-level `.yml` or `.yaml` playbook exists. A test-only change does not trigger the current hook.
- It operates on the current working tree rather than an isolated checkout; unstaged changes can therefore affect pipeline execution.
- It uses the credentials and network access available to the local user running Git.

## Change workflow

### 1. Create a branch

Start from the current `main` branch and create a branch for the proposed network change:

```bash
git switch main
git pull --ff-only origin main
git switch -c change/<change-name>
```

The hook intentionally skips commits made on `main`. Perform pipeline work on a separate branch.

### 2. Configure credentials

The included Ansible inventory examples and pyATS testbeds read credentials from `CISCO_USER` and `CISCO_PASS`. Export them in the shell before committing or running pipeline commands:

```bash
export CISCO_USER='<username>'
export CISCO_PASS='<password>'
```

Do not commit credentials. The hook inherits environment variables from the process that runs `git commit`.

### 3. Configure the Ansible inventory

Inventory examples are stored under `inventory/library/`. The repository currently provides:

- `inventory/library/inventory.yml` for direct network CLI connections.
- `inventory/library/inventory_consoles.yml` for CML console connections.

Select the appropriate example and copy it to the top level of `inventory/`. The local pipeline and all documented Ansible commands use only `inventory/inventory.yml`:

```bash
cp inventory/library/inventory.yml inventory/inventory.yml
```

Modify the copied `inventory/inventory.yml` for the target environment. Define the required groups and hosts, set each management address or console endpoint and ensure that group names match the `hosts` values used by the selected playbooks.

Shared connection settings and credential lookups are defined in each inventory example under the applicable group's `vars` mapping. Keep these variables with the corresponding group when modifying the copied inventory. Credentials must continue to reference `CISCO_USER` and `CISCO_PASS`; do not place literal credentials in the inventory.

The top-level `inventory/inventory.yml` must exist before committing a change that invokes the pipeline. Review its host and group hierarchy before committing:

```bash
uv run ansible-inventory -i inventory/inventory.yml --graph
```

Display the resolved variables for a specific device when validating inventory behavior:

```bash
uv run ansible-inventory -i inventory/inventory.yml \
  --host <device-name>
```

### 4. Configure an optional backup playbook

The pipeline searches the top level of `playbooks/` for the first `.yml` or `.yaml` file whose name contains `backup`. To enable configuration backup, copy the appropriate example:

```bash
cp playbooks/library/backup.yml playbooks/backup.yml
```

Backup playbooks are excluded from deployment. If multiple top-level filenames contain `backup`, only the first matching file is run. Ensure that the selected backup playbook's `hosts` value exists in `inventory/inventory.yml`.

The backup runs before Git creates the commit and uses `inventory/inventory.yml`. A backup failure stops the commit. Generated `*.cfg` files under `backups/` are ignored by Git and must not be committed.

To test a backup playbook explicitly:

```bash
uv run ansible-playbook --syntax-check \
  -i inventory/inventory.yml playbooks/backup.yml
uv run ansible-playbook \
  -i inventory/inventory.yml playbooks/backup.yml
```

### 5. Configure optional save and rollback utilities

Templates for configuration persistence and rollback are stored under `playbooks/utils/library/`. They are disabled until copied directly into `playbooks/utils/`.

To save a rollback baseline before deployment and persist the validated configuration after testing, enable `commit_config.yml`:

```bash
cp playbooks/utils/library/commit_config.yml \
  playbooks/utils/commit_config.yml
```

To restore the saved startup configuration after a deployment or pyATS failure, enable `rollback_config.yml`:

```bash
cp playbooks/utils/library/rollback_config.yml \
  playbooks/utils/rollback_config.yml
```

Edit the `hosts` value in each copied utility so it targets the inventory group affected by the deployment. The group must exist in `inventory/inventory.yml`. The supplied templates use `all_devices`:

```yaml
- name: Commit Configuration
  hosts: all_devices
```

The supplied `commit_config.yml` template executes `write memory`. The supplied `rollback_config.yml` template executes `configure replace nvram:startup-config force`. Review these commands for compatibility with the target platform before enabling the utilities.

Enable both utilities when rollback must use a baseline captured immediately before deployment. Their behavior is independent:

- With both files present, the pipeline saves the pre-deployment configuration, rolls back deployment or pyATS failures and saves the final configuration after successful validation.
- With only `commit_config.yml`, the pipeline saves a baseline before deployment and saves the final configuration after successful validation, but cannot automatically roll back a deployment or pyATS failure.
- With only `rollback_config.yml`, failures restore the startup configuration that existed before the pipeline; the pipeline does not first overwrite it with the current running configuration.
- With neither file, deployment and validation still run, but the pipeline neither saves nor rolls back device configurations.

Remove an active utility from `playbooks/utils/` to disable that capability. Do not copy utility playbooks into the top level of `playbooks/`, where they would be treated as deployment playbooks.

Validate enabled utilities and their target groups before committing:

```bash
uv run ansible-playbook --syntax-check \
  -i inventory/inventory.yml playbooks/utils/commit_config.yml
uv run ansible-playbook --syntax-check \
  -i inventory/inventory.yml playbooks/utils/rollback_config.yml
```

### 6. Configure deployment playbooks

Create or copy deployment playbooks into the top level of `playbooks/`:

```bash
cp playbooks/library/configuration.yml playbooks/configuration.yml
```

The pre-commit pipeline processes top-level `.yml` and `.yaml` files. Files with names containing `backup` are skipped during deployment. Files under `playbooks/library/` and `playbooks/utils/` are not included in the deployment loop; the pipeline invokes utility playbooks separately.

All deployment and enabled utility playbooks use `inventory/inventory.yml`. Review the active inventory, utility target groups and the effect of every playbook before committing because deployment occurs before Git creates the commit.

Validate a playbook manually when needed:

```bash
uv run ansible-playbook --syntax-check \
  -i inventory/inventory.yml playbooks/configuration.yml
```

### 7. Configure pyATS (optional)

The pre-commit pipeline runs pyATS only when `tests/job.py` exists. Create that file or copy and modify the example from `tests/library/`:

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

Run the same pyATS command used by the pre-commit pipeline:

```bash
uv run pyats run job tests/job.py --no-mail --no-archive
```

Remove `tests/job.py` when pyATS validation is not required.

### 8. Review and commit the change

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

The pre-commit hook runs the complete pipeline before the commit is created. If every enabled stage succeeds, Git creates the commit. If a deployment or pyATS stage fails, Git rejects the commit. The pipeline also attempts to restore the startup configuration when `playbooks/utils/rollback_config.yml` is enabled. Pipeline progress is printed to the terminal.

Do not use `git add .` without verifying that no credentials, generated output, or unrelated files will be included.

### 9. Review pipeline results

The pipeline writes command output under `logs/` using the current `HEAD` commit SHA in each stage-specific filename:

- `logs/ansible-pre-cicd-<commit>.log` contains syntax-check, backup, deployment and any enabled save or rollback output.
- `logs/pyats-pre-cicd-<commit>.log` contains pyATS output.
- `logs/git-hooks.log` contains consolidated hook and pipeline console output with terminal color codes removed.

The hook also reports progress and completion status in the terminal. Inspect the applicable logs when a stage reports a failure. Because the hook runs before Git creates the proposed commit, the SHA in these log filenames identifies the current `HEAD`, not the new commit being attempted.

A failed rollback causes the pipeline to exit with a nonzero status and reject the commit, but device state may require manual verification. When `playbooks/utils/commit_config.yml` is enabled, a successful pipeline saves the validated running configuration before allowing Git to create the commit. Without that utility, the pipeline does not persist the validated running configuration.

If the final `commit_config.yml` execution fails, the `commit_config` function exits immediately and does not invoke `rollback_config.yml`. In that case, Git rejects the commit, but deployed running-configuration changes may remain on the devices and require manual review.

### 10. Push the change branch to a remote repository (optional)

If the project uses a remote Git repository, push the change branch after reviewing the commit and local pipeline results. First confirm the current branch and working-tree status:

```bash
git branch --show-current
git status
```

The following example pushes the change branch to a remote named `origin` and configures its upstream tracking branch:

```bash
git push --set-upstream origin change/<change-name>
```

Replace `change/<change-name>` with the actual local branch name and `origin` with the configured remote name when different. After the upstream is configured, subsequent commits can be pushed with:

```bash
git push
```

This step is not required when the repository is used only locally. Pushing does not invoke the local `pre-commit` hook; it runs only when a local commit is attempted.
