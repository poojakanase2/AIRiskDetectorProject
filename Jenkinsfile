pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git'
            }
        }
        stage('Build') {
            steps {
                dir('backend') {
                    sh 'python3 -m pip install -r requirements.txt --break-system-packages'
                    sh 'pytest'
                }
                dir('frontend') {
                    sh 'echo "No build needed for vanilla JS frontend"'
                }
            }
        }
        stage('Code Scan') {
            steps {
                dir('backend') {
                    sh 'pylint app/'
                }
            }
        }
        stage('Docker Build') {
            steps {
                dir('backend') {
                    sh 'docker build -t inventory-backend:latest .'
                }
                dir('frontend') {
                    sh 'docker build -t inventory-frontend:latest .'
                }
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                // Add your deployment steps here
            }
        }
    }
    post {
        failure {
            echo 'Pipeline failed'
        }
    }
}
