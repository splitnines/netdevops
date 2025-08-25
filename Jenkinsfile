pipeline {
    agent any

    environment {
        VENV = ".venv"
    }

    stages {
        stage('Setup Python') {
            environment {
                CISCO_CREDS = credentials('cisco_creds')
            }
            steps {
                dir("${WORKSPACE}") {
                    sh '''
                        export CISCO_USER=$CISCO_CREDS_USR
                        export CISCO_PASS=$CISCO_CREDS_PSW 
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
                sh '''
                    . $VENV/bin/activate
                    ansible-playbook --syntax-check playbooks/*.yml -i inventory/lab.yml
                '''
            }
        }

        stage('Backup') {
            steps {
                sh '''
                    . $VENV/bin/activate
                    ansible-playbook -i inventory/lab.yml playbooks/01_config_backup.yml
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    . $VENV/bin/activate
                    ansible-playbook -i inventory/lab.yml playbooks/02_ntp_config.yml
                '''
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    . $VENV/bin/activate
                    pyats run job tests/job.py --no-mail --no-archive
                '''
            }
        }
    }

    // post {
    //     always {
    //         script {
    //             def commitSha = sh(returnStdout: true, script: "git rev-parse HEAD").trim()
    //
    //             githubNotify(
    //                 context: 'CI Pipeline',
    //                 account: 'splitnines',
    //                 repo: 'netdevops',
    //                 sha: commitSha,
    //                 credentialsId: 'NetDevOps',
    //                 status: currentBuild.currentResult == 'SUCCESS' ? 'SUCCESS' : 'FAILURE',
    //                 description: "Build finished with status ${currentBuild.currentResult}"
    //             )
    //         }
    //     }
    // }
}
