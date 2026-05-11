pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }
        stage('Lint') {
            steps {
                echo 'Running flake8 lint...'
                sh '''
                    python3 -m pip install flake8 --break-system-packages
                    python3 -m flake8 . --exit-zero
                '''
            }
        }
        stage('Test') {
            steps {
                echo 'Running backend tests...'
                sh '''
                    cd backend
                    python3 -m pip install -r requirements.txt --break-system-packages
                    python3 -m pytest || [ $? -eq 5 ]
                '''
            }
        }
        stage('Docker Build') {
            steps {
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
                // Add deployment steps here
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
