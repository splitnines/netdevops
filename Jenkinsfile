pipeline {
    agent any

    environment {
        VENV = ".venv"
    }

    stages {
        stage('Setup Python') {
            steps {
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
            }
        }

        stage('Prepare Logs') {
            steps {
                dir("${WORKSPACE}") {
                    sh '''
                        mkdir -p logs
                        chmod 777 logs
                    '''
                }
            }
        }

        stage('Validate') {
            steps {
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
            }
        }

        stage('Backup') {
            steps {
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
            }
        }

        stage('Deploy') {
            steps {
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
            }
        }

        stage('Tests') {
            steps {
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
            }
        }
    }

    post {
        always {
            githubNotify context: 'CI Pipeline', status: currentBuild.currentResult
        }
    }
}
