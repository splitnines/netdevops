pipeline {
    agent any

    environment {
        VENV = ".venv"
    }

    options {
        // This allows Jenkins to update GitHub commit status
        githubNotify(credentialsId: 'github-pat')
    }

    stages {
        stage('Setup Python') {
            steps {
                githubNotify context: 'Setup Python', status: 'PENDING'
                withCredentials([usernamePassword(
                    credentialsId: 'cisco_creds',
                    usernameVariable: 'CISCO_USER',
                    passwordVariable: 'CISCO_PASS'
                )]) {
                    dir("${WORKSPACE}") {
                        sh '''
                            apt-get update
                            apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip build-essential libssl-dev libffi-dev libssh-dev cmake pkg-config
                            python3.11 -m venv $VENV
                            . $VENV/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }
                githubNotify context: 'Setup Python', status: 'SUCCESS'
            }
        }

        stage('Prepare Logs') {
            steps {
                githubNotify context: 'Prepare Logs', status: 'PENDING'
                dir("${WORKSPACE}") {
                    sh '''
                        mkdir -p logs
                        chmod 777 logs
                    '''
                }
                githubNotify context: 'Prepare Logs', status: 'SUCCESS'
            }
        }

        stage('Validate') {
            steps {
                githubNotify context: 'Validate', status: 'PENDING'
                withCredentials([usernamePassword(
                    credentialsId: 'cisco_creds',
                    usernameVariable: 'CISCO_USER',
                    passwordVariable: 'CISCO_PASS'
                )]) {
                    sh '''
                        . $VENV/bin/activate
                        ansible-playbook --syntax-check playbooks/*.yml -i inventory/lab.yml
                    '''
                }
                githubNotify context: 'Validate', status: 'SUCCESS'
            }
        }

        stage('Backup') {
            steps {
                githubNotify context: 'Backup', status: 'PENDING'
                withCredentials([usernamePassword(
                    credentialsId: 'cisco_creds',
                    usernameVariable: 'CISCO_USER',
                    passwordVariable: 'CISCO_PASS'
                )]) {
                    sh '''
                        . $VENV/bin/activate
                        ansible-playbook -i inventory/lab.yml playbooks/01_config_backup.yml
                    '''
                }
                githubNotify context: 'Backup', status: 'SUCCESS'
            }
        }

        stage('Deploy') {
            steps {
                githubNotify context: 'Deploy', status: 'PENDING'
                withCredentials([usernamePassword(
                    credentialsId: 'cisco_creds',
                    usernameVariable: 'CISCO_USER',
                    passwordVariable: 'CISCO_PASS'
                )]) {
                    sh '''
                        . $VENV/bin/activate
                        ansible-playbook -i inventory/lab.yml playbooks/02_ntp_config.yml
                    '''
                }
                githubNotify context: 'Deploy', status: 'SUCCESS'
            }
        }

        stage('Tests') {
            steps {
                githubNotify context: 'Tests', status: 'PENDING'
                withCredentials([usernamePassword(
                    credentialsId: 'cisco_creds',
                    usernameVariable: 'CISCO_USER',
                    passwordVariable: 'CISCO_PASS'
                )]) {
                    sh '''
                        . $VENV/bin/activate
                        pyats run job tests/job.py --no-mail --no-archive
                    '''
                }
                githubNotify context: 'Tests', status: 'SUCCESS'
            }
        }
    }

    post {
        failure {
            githubNotify status: 'FAILURE'
        }
    }
}
