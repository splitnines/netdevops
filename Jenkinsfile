pipeline {
    agent any
    environment {
        CISCO_USER = credentials('cisco_user')
        CISCO_PASS = credentials('cisco_pass')
        PATH = "$HOME/.cargo/bin:$PATH"
    }
    stages {
        stage('Setup tools') {
            steps {
                sh '''
                    if ! command -v uv >/dev/null 2>&1; then
                        echo "[+] Installing uv"
                        curl -LsSf https://astral.sh/uv/install.sh | sh
                    else
                        echo "[+] uv already installed"
                    fi
                '''
            }
        }
        stage('Validate') {
            steps {
                sh '''
                    export PATH=$HOME/.cargo/bin:$PATH
                    uv sync
                    uv run ansible-playbook --syntax-check playbooks/*.yml -i inventory/lab.yml
                '''
            }
        }
        stage('Backup') {
            steps {
                sh '''
                    export PATH=$HOME/.cargo/bin:$PATH
                    uv run ansible-playbook -i inventory/lab.yml playbooks/01_config_backup.yml
                '''
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    export PATH=$HOME/.cargo/bin:$PATH
                    uv run ansible-playbook -i inventory/lab.yml playbooks/02_ntp_config.yml
                '''
            }
        }
        stage('Tests') {
            steps {
                sh '''
                    export PATH=$HOME/.cargo/bin:$PATH
                    uv run pyats run job tests/job.py --no-mail --no-archive
                '''
            }
        }
    }
}

