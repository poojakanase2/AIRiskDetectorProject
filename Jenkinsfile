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
                echo 'Building application...'
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn clean package
                    else
                        echo "Maven (mvn) is not installed on this runner, skipping build."
                    fi
                '''
            }
        }
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    python3 -m pip install -r ./backend/requirements.txt --break-system-packages
                    python3 -m flake8 ./backend --exit-zero
                    python3 -m pytest ./backend || [ $? -eq 5 ]
                '''
            }
        }
        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    if command -v docker >/dev/null 2>&1; then
                        docker build -t airiskdetector-backend ./backend
                    else
                        echo "Docker is not installed on this runner, skipping Docker build."
                    fi
                '''
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                    echo "Deployment logic goes here."
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
