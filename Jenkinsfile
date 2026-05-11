pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }
        stage('Build') {
            steps {
                echo 'Compiling application...'
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn clean package
                    else
                        echo "Maven is not installed on this runner, skipping Maven build."
                    fi
                '''
            }
        }
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    if command -v python3 >/dev/null 2>&1; then
                        python3 -m pip install -r ./backend/requirements.txt --break-system-packages
                        python3 -m pytest || [ $? -eq 5 ]
                    else
                        echo "Python3 is not installed on this runner, skipping tests."
                    fi
                '''
            }
        }
        stage('Archive') {
            steps {
                echo 'Archiving artifacts...'
                archiveArtifacts artifacts: '**/target/*.jar', fingerprint: true, onlyIfSuccessful: true
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                    if command -v docker >/dev/null 2>&1; then
                        docker build -t airiskdetector-backend ./backend
                    else
                        echo "Docker is not installed on this runner, skipping Docker build."
                    fi
                '''
            }
        }
    }
    post {
        always {
            echo 'Cleaning workspace...'
            cleanWs()
        }
    }
}
