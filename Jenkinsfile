pipeline {
    agent any
    environment {
        CISCO_USER = credentials('cisco_user')   // stored in Jenkins credentials
        CISCO_PASS = credentials('cisco_pass')
    }
    stages {
        stage('Validate') {
            steps {
                sh 'uv sync'
                sh 'uv run ansible-playbook --syntax-check playbooks/*.yml -i inventory/lab.yml'
            }
        }
        stage('Backup') {
            steps {
                sh 'uv run ansible-playbook -i inventory/lab.yml playbooks/01_config_backup.yml'
            }
        }
        stage('Deploy') {
            steps {
                sh 'uv run ansible-playbook -i inventory/lab.yml playbooks/02_ntp_config.yml'
            }
        }
        stage('Tests') {
            steps {
                sh 'uv run pyats run job tests/job.py --no-mail --no-archive'
            }
        }
    }
}
