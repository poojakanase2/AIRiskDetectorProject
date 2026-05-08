pipeline {
    agent any
    environment {
        BACKEND_DIR = './backend'
        FRONTEND_DIR = './frontend'
    }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }
        stage('Lint') {
            steps {
                dir(env.BACKEND_DIR) {
                    sh 'python3 -m pip install flake8 --break-system-packages'
                    sh 'python3 -m flake8 . --exit-zero'
                }
            }
        }
        stage('Test') {
            steps {
                dir(env.BACKEND_DIR) {
                    sh 'python3 -m pip install pytest --break-system-packages'
                    sh 'python3 -m pytest'
                }
            }
        }
        stage('Docker Build') {
            steps {
                dir(env.BACKEND_DIR) {
                    sh 'docker build -t airiskdetector-backend .'
                }
                dir(env.FRONTEND_DIR) {
                    sh 'docker build -t airiskdetector-frontend .'
                }
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
        always {
            echo 'Pipeline finished.'
        }
        failure {
            echo 'Pipeline failed.'
        }
        success {
            echo 'Pipeline succeeded.'
        }
    }
}
