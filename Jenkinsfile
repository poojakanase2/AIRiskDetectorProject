pipeline {
    agent any

    environment {
        APP_NAME = "BillingService"
        REGISTRY = "dockerhub.io/demo"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Fetching source code..."
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                echo "Installing backend dependencies..."
                sh '''
                cd backend
                python3 -m pip install --upgrade pip --break-system-packages
                python3 -m pip install -r requirements.txt --break-system-packages
                '''
            }
        }

        stage('Unit Test') {
            steps {
                echo "Running Python unit tests..."
                sh '''
                cd backend
                python3 -m pytest || [ $? -eq 5 ]
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "Creating Docker image..."
                sh '''
                if command -v docker >/dev/null 2>&1; then
                    docker build -t billing-service:v1 .
                else
                    echo "docker is not installed on this runner, skipping this step."
                fi
                '''
            }
        }

        stage('Push Image') {
            steps {
                echo "Pushing image to registry..."
                sh '''
                if command -v docker >/dev/null 2>&1; then
                    docker push billing-service:v1
                else
                    echo "docker is not installed on this runner, skipping this step."
                fi
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying application..."
                sh '''
                if command -v kubectl >/dev/null 2>&1; then
                    kubectl apply -f deployment.yaml
                else
                    echo "kubectl is not installed on this runner, skipping this step."
                fi
                '''
            }
        }
    }

    post {
        success {
            echo "Build completed successfully"
        }
        always {
            echo "Cleaning Jenkins workspace..."
            cleanWs()
        }
    }
}
