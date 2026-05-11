pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                echo 'Pulling source code from GitHub...'
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }
        stage('Build') {
            steps {
                echo 'Building application...'
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn clean install
                    else
                        echo "Maven is not installed on this runner, skipping Maven build."
                    fi
                '''
            }
        }
        stage('Static Analysis') {
            steps {
                echo 'Running static analysis...'
                sh '''
                    if command -v flake8 >/dev/null 2>&1; then
                        python3 -m flake8 ./backend --exit-zero
                    else
                        echo "flake8 is not installed, skipping lint."
                    fi
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
        stage('Push Image') {
            steps {
                echo 'Pushing Docker image...'
                sh '''
                    if command -v docker >/dev/null 2>&1; then
                        echo "Push logic here (e.g., docker push)"
                    else
                        echo "Docker is not installed on this runner, skipping Docker push."
                    fi
                '''
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                    echo "Deploy logic here (e.g., kubectl apply)"
                '''
            }
        }
    }
    post {
        failure {
            echo 'Deployment failed'
        }
    }
}
