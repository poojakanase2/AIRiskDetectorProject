pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }
        stage('Build') {
            steps {
                echo 'Installing backend dependencies...'
                sh '''cd backend
python3 -m pip install --upgrade pip --break-system-packages
python3 -m pip install -r requirements.txt --break-system-packages'''
            }
        }
        stage('Lint') {
            steps {
                echo 'Linting backend...'
                sh '''cd backend
python3 -m pip install flake8 --break-system-packages
python3 -m flake8 . --exit-zero'''
            }
        }
        stage('Test') {
            steps {
                echo 'Running backend tests...'
                sh '''cd backend
python3 -m pip install pytest --break-system-packages
python3 -m pytest || [ $? -eq 5 ]'''
            }
        }
        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t airisk-backend:latest backend/'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                // Add deployment commands here as needed
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
