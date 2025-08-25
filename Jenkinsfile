def runStage() {
    def changedFiles = sh(
        script: "git diff --name-only HEAD~1 HEAD",
        returnStdout: true
    ).trim().split("\n")

    return changedFiles.any {
        it.startsWith("playbooks/") ||
        it.startsWith("configs/")  ||
        it.startsWith("test/")
    }
}

pipeline {
    agent any


    environment {
        VENV = ".venv"
        CISCO_CREDS = credentials('cisco_creds')
    }

    stages {
        stage('Setup Python') {
            when {
                expression {
                    def changedFiles = sh(
                        script: "git diff --name-only HEAD~1 HEAD",
                        returnStdout: true
                    ).trim().split("\n")

                    return changedFiles.any {
                        it.startsWith("playbooks/") ||
                        it.startsWith("configs/") ||
                        it.startsWith("test/")
                    }
                }
            }
            steps {
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

        stage('Prepare Logs') {
            when {
                expression {
                    def changedFiles = sh(
                        script: "git diff --name-only HEAD~1 HEAD",
                        returnStdout: true
                    ).trim().split("\n")

                    return changedFiles.any {
                        it.startsWith("playbooks/") ||
                        it.startsWith("configs/") ||
                        it.startsWith("test/")
                    }
                }
            }
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
            when {
                expression {
                    def changedFiles = sh(
                        script: "git diff --name-only HEAD~1 HEAD",
                        returnStdout: true
                    ).trim().split("\n")

                    return changedFiles.any {
                        it.startsWith("playbooks/") ||
                        it.startsWith("configs/") ||
                        it.startsWith("test/")
                    }
                }
            }
            steps {
                sh '''
                    export CISCO_USER=$CISCO_CREDS_USR
                    export CISCO_PASS=$CISCO_CREDS_PSW 
                    . $VENV/bin/activate
                    for file in $(find playbooks/ -type f -name "*.yml"); do
                      echo ">>> Syntax Check $file"
                      ansible-playbook --syntax-check "$file" -i inventory/lab.yml || exit 1
                      echo ">>> Check $file"
                      ansible-playbook --check "$file" -i inventory/lab.yml || exit 1
                    done
                '''
            }
        }

        stage('Backup') {
            when {
                expression {
                    def changedFiles = sh(
                        script: "git diff --name-only HEAD~1 HEAD",
                        returnStdout: true
                    ).trim().split("\n")

                    return changedFiles.any {
                        it.startsWith("playbooks/") ||
                        it.startsWith("configs/") ||
                        it.startsWith("test/")
                    }
                }
            }
            steps {
                sh '''
                    export CISCO_USER=$CISCO_CREDS_USR
                    export CISCO_PASS=$CISCO_CREDS_PSW 
                    . $VENV/bin/activate
                    ansible-playbook -i inventory/lab.yml playbooks/01_config_backup.yml
                '''
            }
        }

        stage('Archive Backups') {
            when {
                expression { runStage() }
            }
            steps {
                archiveArtifacts artifacts: 'backups/*.log', fingerprint: true
            }
        }

        stage('Deploy') {
            when {
                expression {
                    def changedFiles = sh(
                        script: "git diff --name-only HEAD~1 HEAD",
                        returnStdout: true
                    ).trim().split("\n")

                    return changedFiles.any {
                        it.startsWith("playbooks/") ||
                        it.startsWith("configs/") ||
                        it.startsWith("test/")
                    }
                }
            }
            steps {
                sh '''
                    export CISCO_USER=$CISCO_CREDS_USR
                    export CISCO_PASS=$CISCO_CREDS_PSW 
                    . $VENV/bin/activate
                    ansible-playbook -i inventory/lab.yml playbooks/02_ntp_config.yml
                '''
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    export CISCO_USER=$CISCO_CREDS_USR
                    export CISCO_PASS=$CISCO_CREDS_PSW 
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
    //                 status: currentBuild.currentResult,
    //                 description: "Build finished with status ${currentBuild.currentResult}"
    //             )
    //         }
    //     }
    // }
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
    //                 status: currentBuild.currentResult,
    //                 description: "Build finished with status ${currentBuild.currentResult}"
    //             )
    //         }
    //     }
    // }
}
