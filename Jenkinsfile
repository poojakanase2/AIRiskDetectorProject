pipeline {
    agent any

    environment {
        PROJECT_NAME = "OrderService"
        IMAGE_TAG = "v1.0"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Pulling source code from GitHub..."
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                echo "Building application..."
                sh 'mvn clean install'
            }
        }

        stage('Static Analysis') {
            steps {
                echo "Running SonarQube analysis..."
                sh 'mvn sonar:sonar'
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image..."
                sh '''
                    if command -v docker >/dev/null 2>&1; then
                        docker build -t orderservice:$IMAGE_TAG .
                    else
                        echo "Docker is not installed on this runner, skipping Docker build."
                    fi
                '''
            }
        }

        stage('Push Image') {
            steps {
                echo "Pushing Docker image..."
                sh '''
                    if command -v docker >/dev/null 2>&1; then
                        docker push orderservice:$IMAGE_TAG
                    else
                        echo "Docker is not installed on this runner, skipping Docker push."
                    fi
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying to Kubernetes..."
                sh '''
                    if command -v kubectl >/dev/null 2>&1; then
                        kubectl apply -f k8s/deployment.yaml
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
            echo "Deployment failed"
        }
    }
}
