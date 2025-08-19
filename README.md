# NetDevOps Pipeline

This repository contains an Ansible + pyATS based NetDevOps pipeline for automating configuration backup, validation, and testing of Cisco IOS-XE devices.

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/splitnines/netdevops.git
cd netdevops
```

### 2. Install dependencies

#### Option A — Using [uv](https://github.com/astral-sh/uv) (preferred)
If you have `uv` installed, you can set up the full environment with:

```bash
uv sync
```

This will install all dependencies defined in `pyproject.toml` and `uv.lock`.

#### Option B — Using pip
If you don’t have `uv`, you can use the pre-generated `requirements.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Environment Variables
Credentials are loaded from environment variables (or an `.env` file):

```bash
CISCO_USER=<your-username>
CISCO_PASS=<your-password>
```

You can copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

### Inventory
Device inventory is defined under `inventory/`.  
Example: `inventory/ospf_lab.yml`

Update this file with the IPs/hostnames of your own devices.

---

## ▶️ Usage

### Backup Configurations
```bash
ansible-playbook -i inventory/ospf_lab.yml playbooks/01_config_backup.yml
```

### Apply NTP Configuration
```bash
ansible-playbook -i inventory/ospf_lab.yml playbooks/02_ntp_config.yml
```

### Run pyATS Job
```bash
uv run pyats run job tests/job.py --testbed testbed.yaml
```

---

## 📂 Project Structure

```
.
├── ansible.cfg              # Ansible configuration
├── backups/                 # Stored device config backups
├── configs/                 # Example configuration snippets
├── inventory/               # Ansible inventory files
├── logs/                    # Ansible logs
├── playbooks/               # Playbooks for automation tasks
├── tests/                   # pyATS test scripts/jobs
├── pyproject.toml           # Project metadata + dependencies (uv)
├── uv.lock                  # uv lockfile (pinned deps)
├── requirements.txt         # pip-compatible dependencies
└── README.md                # This file
```

---

## 🛠 Development

Run linting and syntax checks:

```bash
yamllint .
ansible-playbook --syntax-check playbooks/*.yml
pytest
```

---

## ✅ Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Cisco IOS-XE devices reachable via SSH

---

## 📄 License
MIT License – see [LICENSE](LICENSE) for details.
