pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }
        stage('Backend Test') {
            steps {
                dir('backend') {
                    sh 'python3 -m pip install -r requirements.txt --break-system-packages'
                    sh 'python3 -m pytest'
                }
            }
        }
        stage('Code Scan') {
            steps {
                dir('backend') {
                    sh 'python3 -m pip install flake8 --break-system-packages'
                    sh 'python3 -m flake8 .'
                }
            }
        }
        stage('Docker Build') {
            steps {
                sh 'docker build -t airiskdetector-backend ./backend'
                sh 'docker build -t airiskdetector-frontend ./frontend'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo Deploying application...'
                // Add actual deploy commands here
            }
        }
    }
    post {
        failure {
            echo 'Pipeline failed'
        }
    }
}