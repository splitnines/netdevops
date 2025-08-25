// Returns a bool based on any changes to the repo in
// predefined directories
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
            when { expression { runStage() } }
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
            when { expression { runStage() } }
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
            when { expression { runStage() } }
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

        stage('Clean Backup Directory') {
            when { expression { runStage() } }
            steps {
                sh '''
                  rm -rf backups
                  mkdir -p backups
                '''
            }
        }

        stage('Backup') {
            when { expression { runStage() } }
            steps {
                sh '''
                    export CISCO_USER=$CISCO_CREDS_USR
                    export CISCO_PASS=$CISCO_CREDS_PSW 
                    . $VENV/bin/activate
                    for file in $(find playbooks/infra/ -type f -name "*.yml"); do
                      echo ">>> Running infra playbook $file"
                      ansible-playbook -i inventory/lab.yml "$file" || exit 1
                    done
                '''
            }
        }

        stage('Archive Backups') {
            when { expression { runStage() } }
            steps {
                archiveArtifacts artifacts: 'backups/*.log', fingerprint: true
            }
        }

        stage('Deploy') {
            when { expression { runStage() } }
            steps {
                sh '''
                    export CISCO_USER=$CISCO_CREDS_USR
                    export CISCO_PASS=$CISCO_CREDS_PSW 
                    . $VENV/bin/activate
                    for file in $(find playbooks/ -type f -name "*.yml"); do
                      echo "Deploying playbook $file"
                      ansible-playbook -i inventory/lab.yml $file || exit 1
                    done
                '''
            }
        }

        stage('Tests') {
            when { expression { runStage() } }
            steps {
                sh '''
                    export CISCO_USER=$CISCO_CREDS_USR
                    export CISCO_PASS=$CISCO_CREDS_PSW 
                    . $VENV/bin/activate
                    pyats run job tests/job.py --no-mail --no-archive
                '''
            }
            post {
                always {
                    script {
                        def sha = sh(returnStdout: true, script: "git rev-parse HEAD").trim()
                        githubNotify(
                            context: "Validate",
                            account: "splitnines",         // your GitHub org/user
                            repo: "netdevops",             // your repo name
                            sha: sha,                      // commit SHA
                            credentialsId: "NetDevOps", // Jenkins credential with PAT or GitHub App token
                            status: currentBuild.currentResult,
                            description: "Pipeline finished with ${currentBuild.currentResult}"
                        )
                    }
                }
            }
        }
    }
}
