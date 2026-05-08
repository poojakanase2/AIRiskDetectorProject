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
                dir('backend') {
                    sh 'python3 -m pip install --upgrade pip --break-system-packages'
                    sh 'python3 -m pip install -r requirements.txt --break-system-packages'
                    sh 'python3 -m pytest'
                }
            }
        }
        stage('Code Scan') {
            steps {
                dir('backend') {
                    sh 'python3 -m pip install flake8 --break-system-packages'
                    sh 'flake8 .'
                }
            }
        }
        stage('Docker Build') {
            steps {
                sh 'docker build -t airisk-backend ./backend'
                sh 'docker build -t airisk-frontend ./frontend'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                // Add your deployment commands here
            }
        }
    }
    post {
        failure {
            echo 'Pipeline failed'
        }
    }
}
