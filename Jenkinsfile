pipeline {
    agent any

    environment {
        SERVICE_NAME = "NotificationService"
        BUILD_NUMBER = "1.0.${env.BUILD_ID}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Downloading source code..."
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                echo "Packaging application..."
                sh '''
                if command -v mvn >/dev/null 2>&1; then
                    mvn clean package
                else
                    echo "Maven is not installed on this runner, skipping build."
                fi
                '''
            }
        }

        stage('Security Scan') {
            steps {
                echo "Running dependency scan..."
                sh '''
                if command -v mvn >/dev/null 2>&1; then
                    mvn dependency-check:check
                else
                    echo "Maven is not installed on this runner, skipping dependency check."
                fi
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image..."
                sh '''
                if command -v docker >/dev/null 2>&1; then
                    docker build -t notification-service:${BUILD_NUMBER} .
                else
                    echo "Docker is not installed on this runner, skipping Docker build."
                fi
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying application to Kubernetes..."
                sh '''
                if command -v kubectl >/dev/null 2>&1; then
                    kubectl apply -f k8s/service.yaml
                else
                    echo "kubectl is not installed on this runner, skipping deployment."
                fi
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline executed successfully"
        }
        failure {
            echo "Pipeline execution failed"
        }
    }
}
