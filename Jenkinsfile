pipeline {
    agent any

    environment {
        APP_NAME = "PaymentService"
        DOCKER_IMAGE = "payment-app"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                echo "Building application..."
                sh 'mvn clean package'
            }
        }

        stage('Test') {
            steps {
                echo "Running unit tests..."
                sh 'mvn test'
            }
        }

        stage('Docker Build') {
            steps {
                echo "Creating Docker image..."
                sh '''
                    if command -v docker >/dev/null 2>&1; then
                        docker build -t payment-app:v1 .
                    else
                        echo "Docker is not installed on this runner, skipping Docker build."
                    fi
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying application..."
                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }

    post {
        success {
            echo "Build completed successfully"
        }
        always {
            echo "Cleaning workspace..."
            cleanWs()
        }
    }
}
